import asyncio
import functools
import json
import logging

from fastapi import APIRouter, Request

from app.services.fred_service import fred
from app.services import tts_service
from app.services.command_parser import command_parser
from app.services.intent_engine import intent_engine
from app.services.alexa_signature import verify_alexa_request
from app.core.homeassistant.client import ha_client

router = APIRouter(prefix="/alexa", tags=["Alexa"])
logger = logging.getLogger(__name__)

# Único Echo da casa por enquanto. Se mais dispositivos forem
# cadastrados, isso precisa vir do próprio request da Alexa.
ALEXA_NOTIFY_ENTITY = "notify.alexa_taiane_speak"

# Este endpoint fica exposto na internet e alguns intents chegam a
# acionar dispositivos reais (portão, luz, ar). Além da assinatura
# criptográfica (verify_alexa_request), essa checagem de applicationId
# garante que é especificamente a NOSSA skill, não outra.
ALEXA_SKILL_ID = "amzn1.ask.skill.c305dea3-8c08-4164-9425-ea85717913cc"

# Só usado no fluxo assíncrono (_answer_async): ninguém fica esperando
# essa resposta na hora, então dá pra tolerar um cold start do Ollama
# (modelo descarregado da memória por inatividade) sem cair no fallback
# de erro à toa.
ASYNC_LLM_TIMEOUT = 120


def _request_application_id(body: dict) -> str | None:
    return (
        body.get("session", {}).get("application", {}).get("applicationId")
        or body.get("context", {}).get("System", {}).get("application", {}).get("applicationId")
    )

# Python só garante que uma task em background roda até o fim se algo
# segurar uma referência a ela — sem isso, o garbage collector pode
# derrubar a task no meio da execução. Esse set guarda essa referência.
_background_tasks: set[asyncio.Task] = set()


def _fire_and_forget(coro):
    task = asyncio.create_task(coro)
    _background_tasks.add(task)
    task.add_done_callback(_background_tasks.discard)
    return task


def _speech_response(text, end_session=True):
    audio_url = tts_service.synthesize(text)

    if audio_url:
        ssml = f'<speak><audio src="{audio_url}"/></speak>'
        output_speech = {
            "type": "SSML",
            "ssml": ssml
        }
    else:
        output_speech = {
            "type": "PlainText",
            "text": text
        }

    return {
        "version": "1.0",
        "response": {
            "outputSpeech": output_speech,
            "shouldEndSession": end_session
        }
    }


async def _answer_async(consulta: str):
    try:
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None, functools.partial(fred.ask, consulta, llm_timeout=ASYNC_LLM_TIMEOUT)
        )
        message = result.get("message", "Não consegui pensar em uma resposta.")

        ha_client.call_service(
            "notify",
            "send_message",
            {
                "entity_id": ALEXA_NOTIFY_ENTITY,
                "message": message
            }
        )
    except Exception:
        logger.exception("Falha ao responder pergunta assíncrona da Alexa")


@router.post("/webhook")
async def alexa_webhook(request: Request):
    raw_body = await request.body()

    try:
        body = json.loads(raw_body)
    except Exception:
        return _speech_response("Não entendi a requisição.")

    valid, reason = verify_alexa_request(
        raw_body,
        body,
        request.headers.get("Signature"),
        request.headers.get("SignatureCertChainUrl"),
    )
    if not valid:
        logger.warning("Alexa webhook: assinatura inválida (%s)", reason)
        return _speech_response("Não autorizado.")

    if _request_application_id(body) != ALEXA_SKILL_ID:
        logger.warning("Alexa webhook: applicationId não confere, requisição rejeitada")
        return _speech_response("Não autorizado.")

    req = body.get("request", {})
    req_type = req.get("type")

    if req_type == "LaunchRequest":
        return _speech_response(
            "Fred pronto. Pode falar o que precisa.",
            end_session=False
        )

    if req_type == "IntentRequest":
        intent = req.get("intent", {})
        intent_name = intent.get("name")

        if intent_name in ("AMAZON.StopIntent", "AMAZON.CancelIntent"):
            return _speech_response("Até mais.")

        slots = intent.get("slots", {})
        consulta = slots.get("consulta", {}).get("value", "")

        if not consulta:
            return _speech_response("Não entendi o que você pediu.")

        # Comandos de dispositivo (regras) respondem na hora.
        # Conversa aberta cai no LLM, que é lento nesse hardware
        # (10-30s) — mais que o limite de resposta da própria Alexa.
        # Nesse caso respondemos na hora e mandamos a resposta de
        # verdade depois, como um anúncio separado.
        parsed = command_parser.parse(consulta)
        classified = intent_engine.parse(parsed)

        if classified.get("type") == "unknown":
            _fire_and_forget(_answer_async(consulta))
            return _speech_response(
                "Deixa eu pensar, já te aviso.",
                end_session=True
            )

        result = fred.ask(consulta)
        message = result.get("message", "Não consegui processar.")

        return _speech_response(message, end_session=False)

    if req_type == "SessionEndedRequest":
        return {
            "version": "1.0",
            "response": {}
        }

    return _speech_response("Não entendi.")
