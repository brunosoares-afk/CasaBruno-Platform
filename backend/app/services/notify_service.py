import base64
import logging

import requests

from app.config.settings import settings
from app.services import voice_service

logger = logging.getLogger("notify_service")
logger.setLevel(logging.INFO)
if not logging.getLogger().handlers:
    # Mesmo gotcha já documentado em whatsapp.py: sem isso o root logger
    # fica sem handler e logger.info() some silenciosamente.
    logging.basicConfig(level=logging.INFO)

BRIDGE_URL = "http://127.0.0.1:8095"
VOICE_TIMEOUT = 30


async def notify(text: str) -> bool:
    """Fred "fala primeiro" — manda texto+voz pro chat próprio do
    WhatsApp, sem ser resposta a nada (usado pelos avisos proativos:
    automações da HA via /fred/notify, e os jobs do scheduler_service).
    Nunca lança — quem chama não deve travar por causa de um aviso que
    falhou, só loga o resultado."""

    payload = {"jid": settings.FRED_NOTIFY_JID, "text": text}

    try:
        audio = await voice_service.synthesize(text)
        payload["audioBase64"] = base64.b64encode(audio).decode("ascii")
        payload["mimetype"] = "audio/ogg; codecs=opus"
    except Exception:
        logger.exception("Falha ao sintetizar voz do aviso proativo — mandando só texto")

    try:
        resp = requests.post(f"{BRIDGE_URL}/send", json=payload, timeout=10)
        resp.raise_for_status()
        logger.info("Aviso proativo enviado: %r", text[:80])
        return True
    except Exception:
        logger.exception("Falha ao enviar aviso proativo pelo WhatsApp")
        return False
