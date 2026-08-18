import asyncio
import base64
import logging
from typing import Optional

import requests
from fastapi import APIRouter
from pydantic import BaseModel

from app.services import voice_service, memory_service
from app.services.command_parser import command_parser
from app.services.fred_memory import memory as fred_memory
from app.services.fred_service import fred
from app.services.intent_engine import intent_engine
from app.services.people_service import resolve_person, is_allowed_whatsapp_sender

router = APIRouter(tags=["WHATSAPP"])
logger = logging.getLogger("whatsapp")
logger.setLevel(logging.INFO)
if not logging.getLogger().handlers:
    # uvicorn só configura os loggers "uvicorn.*" por padrão — sem isso
    # o root logger fica sem handler e todo logger.info() daqui some
    # (o "handler de último recurso" do Python só mostra WARNING+).
    logging.basicConfig(level=logging.INFO)

VOICE_TIMEOUT = 90  # Kokoro (voz padrão desde 2026-08-18) é ~2.3x mais lento que tempo real nesta CPU
LLM_TIMEOUT = 180  # Ollama nessa CPU (sem AVX) varia muito, 35-60s no normal, pode passar de 120s
BRIDGE_URL = "http://127.0.0.1:8095"


class WhatsAppIncoming(BaseModel):
    sender: str
    pushName: Optional[str] = ""
    text: Optional[str] = None
    audioBase64: Optional[str] = None
    mimetype: Optional[str] = None


def _will_fall_to_llm(text: str, sender: str) -> bool:
    person = resolve_person("whatsapp", sender)

    # Só espia se existe confirmação pendente, sem consumi-la — intent_engine.parse()
    # tem o efeito colateral de esquecer a confirmação assim que reconhece um
    # "sim"/"não", e essa função é só uma prévia (decide se manda o aviso de
    # "pensando") cujo resultado é descartado. Chamar parse() aqui de verdade
    # consumiria a confirmação e o processamento real, logo depois, não acharia
    # mais nada — reproduzido ao vivo 2026-08-16: "sim" respondia com o
    # fallback do LLM em vez de executar a ação combinada.
    if person and fred_memory.recall_fresh(person, "pending_confirmation", 600):
        return False

    parsed = command_parser.parse(text)
    intent = intent_engine.parse(parsed, person=person)
    return intent.get("type") == "unknown"


def _notify_thinking(sender: str) -> None:
    try:
        requests.post(
            f"{BRIDGE_URL}/send",
            json={"jid": sender, "text": "🤔 Pensando... isso pode demorar um pouco."},
            timeout=5,
        )
    except Exception:
        logger.exception("Falha ao mandar aviso de 'pensando'")


async def _ask_fred(text: str, sender: str) -> str:
    if _will_fall_to_llm(text, sender):
        await asyncio.to_thread(_notify_thinking, sender)

    result = await asyncio.to_thread(fred.ask, text, LLM_TIMEOUT, "whatsapp", sender)
    return result.get("message") or "Não consegui responder agora."


async def _reply_with_voice(display_text: str, speak_text: str, sender: str = None) -> dict:
    """Monta a resposta com texto + (se der) uma nota de voz do speak_text,
    na voz preferida da pessoa (Fase 6.3), se ela tiver uma salva."""

    response = {"text": display_text}

    person = resolve_person("whatsapp", sender)
    voice = memory_service.get_preference(person, "voice")

    try:
        audio_reply = await asyncio.wait_for(
            voice_service.synthesize(speak_text, voice), timeout=VOICE_TIMEOUT
        )
        response["audioBase64"] = base64.b64encode(audio_reply).decode("ascii")
        response["mimetype"] = "audio/ogg; codecs=opus"
        logger.info("TTS ok: %d bytes de áudio gerados", len(audio_reply))
    except Exception:
        logger.exception("Falha ao sintetizar áudio de resposta — mandando só texto")

    return response


@router.get("/whatsapp/status")
def status():
    try:
        r = requests.get(f"{BRIDGE_URL}/status", timeout=5)
        r.raise_for_status()
        return r.json()
    except Exception:
        return {"connected": False, "hasQr": False, "selfJid": None}


@router.post("/whatsapp/incoming")
async def incoming(data: WhatsAppIncoming):

    logger.info(
        "Recebido de %s: %s",
        data.sender,
        f"texto={data.text!r}" if data.text else f"audio ({data.mimetype})",
    )

    if not is_allowed_whatsapp_sender(data.sender):
        logger.warning("Remetente fora da allowlist, ignorado: %s", data.sender)
        return {"text": None}

    if data.text:
        message = await _ask_fred(data.text, data.sender)
        return await _reply_with_voice(message, message, data.sender)

    if data.audioBase64:
        audio_bytes = base64.b64decode(data.audioBase64)

        try:
            text = await asyncio.wait_for(
                voice_service.transcribe(audio_bytes), timeout=VOICE_TIMEOUT
            )
        except Exception:
            return {
                "text": (
                    "Não consegui entender esse áudio — tenta de novo ou "
                    "manda por texto."
                )
            }

        if not text:
            return {"text": "Não consegui entender o que você disse no áudio."}

        message = await _ask_fred(text, data.sender)

        return await _reply_with_voice(f'🎤 "{text}"\n\n{message}', message, data.sender)

    return {"text": "Não entendi a mensagem."}
