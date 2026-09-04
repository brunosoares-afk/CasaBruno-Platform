import base64
import io
import logging
import wave

import requests

from app.config.settings import settings

logger = logging.getLogger(__name__)

_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

# gemini-3.1-flash-tts-preview (mais novo) devolveu 503 "alta demanda" de
# forma consistente em teste (2026-09-04) — fica no 2.5, estável e coberto
# pela mesma chave free-tier do texto.
_TTS_MODEL = "gemini-2.5-flash-preview-tts"
TTS_VOICE = "Kore"


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


def synthesize(text: str, voice: str = TTS_VOICE, timeout: int = 30) -> bytes:
    """Texto -> wav (bytes) via Gemini TTS. ~3-4s de latência por frase
    curta (rede + geração) contra quase instantâneo do Piper local — ver
    [[casa-bruno-gemini-voz-completa-2026-09-04]]. Levanta exceção em
    qualquer falha; quem chama decide o fallback (mesmo padrão de generate())."""

    if not settings.GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY não configurada")

    resp = requests.post(
        _URL.format(model=_TTS_MODEL),
        params={"key": settings.GEMINI_API_KEY},
        json={
            "contents": [{"parts": [{"text": text}]}],
            "generationConfig": {
                "responseModalities": ["AUDIO"],
                "speechConfig": {
                    "voiceConfig": {"prebuiltVoiceConfig": {"voiceName": voice}}
                },
            },
        },
        timeout=timeout,
    )
    resp.raise_for_status()
    data = resp.json()

    candidates = data.get("candidates") or []
    if not candidates:
        raise RuntimeError(f"Gemini TTS sem candidatos: {data}")

    parts = candidates[0].get("content", {}).get("parts", [])
    inline = parts[0].get("inlineData") if parts else None
    if not inline or not inline.get("data"):
        raise RuntimeError(f"Gemini TTS sem áudio: {data}")

    pcm = base64.b64decode(inline["data"])

    # mimeType vem como "audio/L16;codec=pcm;rate=24000" — 16-bit mono.
    rate = 24000
    mime = inline.get("mimeType", "")
    if "rate=" in mime:
        try:
            rate = int(mime.split("rate=")[1].split(";")[0])
        except ValueError:
            pass

    buf = io.BytesIO()
    with wave.open(buf, "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(rate)
        wav_file.writeframes(pcm)

    return buf.getvalue()
