import logging

import requests

from app.config.settings import settings

logger = logging.getLogger(__name__)

_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"


def is_configured() -> bool:
    return bool(settings.GEMINI_API_KEY)


def generate(system: str, prompt: str, timeout: int = 30) -> str:
    """Chama o Gemini (papo livre do Fred — ver
    [[casa-bruno-voice-quality-2026-08-21]]: o modelo local pequeno
    ignorava a pergunta/alucinava/vazava prompt em conversa aberta).
    Levanta exceção em qualquer falha — quem chama decide o fallback."""

    if not settings.GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY não configurada")

    resp = requests.post(
        _URL.format(model=settings.GEMINI_MODEL),
        params={"key": settings.GEMINI_API_KEY},
        json={
            "systemInstruction": {"parts": [{"text": system}]},
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        },
        timeout=timeout,
    )
    resp.raise_for_status()
    data = resp.json()

    candidates = data.get("candidates") or []
    if not candidates:
        raise RuntimeError(f"Gemini sem candidatos: {data}")

    parts = candidates[0].get("content", {}).get("parts", [])
    text = "".join(p.get("text", "") for p in parts).strip()

    if not text:
        raise RuntimeError(f"Gemini retornou texto vazio: {data}")

    return text
