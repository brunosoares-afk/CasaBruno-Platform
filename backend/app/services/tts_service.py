import asyncio
import subprocess
import uuid
import os
import time
from pathlib import Path

from app.services import gemini_service, voice_service

AUDIO_DIR = Path("/opt/CasaBruno-Platform/backend/tts_audio")
PUBLIC_BASE_URL = "https://hda08fx9s7v.sn.mynetname.net/alexa/audio"

# A Alexa derruba o skill se o webhook não responder em poucos segundos —
# por isso o Gemini TTS entra com timeout curto (5s) aqui, diferente dos
# outros canais. Se estourar isso ou falhar, cai pro Piper local (nunca
# o Kokoro, que já era descartado por ser ~2x mais lento que tempo real
# nesta CPU — ver voice_service.py). Ver [[casa-bruno-gemini-voz-completa-2026-09-04]].
TTS_VOICE = "pt_BR-cadu-medium"
GEMINI_TIMEOUT = 5

AUDIO_DIR.mkdir(parents=True, exist_ok=True)


def _cleanup_old_files(max_age_seconds=3600):
    now = time.time()
    for f in AUDIO_DIR.glob("*.mp3"):
        try:
            if now - f.stat().st_mtime > max_age_seconds:
                f.unlink()
        except Exception:
            pass


def synthesize(text):
    """Gera audio MP3 (48kbps, 16000Hz) a partir de texto, usando o Piper
    local. Retorna a URL publica do arquivo gerado."""

    _cleanup_old_files()

    file_id = uuid.uuid4().hex
    raw_path = f"/tmp/fred_tts_{file_id}.wav"
    mp3_path = str(AUDIO_DIR / f"{file_id}.mp3")

    try:
        try:
            wav_bytes = gemini_service.synthesize(text, timeout=GEMINI_TIMEOUT)
        except Exception:
            wav_bytes = asyncio.run(voice_service.piper_tts(text, TTS_VOICE))

        with open(raw_path, "wb") as f:
            f.write(wav_bytes)

        try:
            subprocess.run(
                [
                    "ffmpeg", "-y",
                    "-i", raw_path,
                    "-af", "adelay=350:all=1,apad=pad_dur=0.3",
                    "-ar", "16000",
                    "-ab", "48k",
                    "-ac", "1",
                    "-write_xing", "0",
                    "-id3v2_version", "0",
                    mp3_path,
                ],
                capture_output=True,
                timeout=20,
            )
        finally:
            if os.path.exists(raw_path):
                os.remove(raw_path)

        if os.path.exists(mp3_path):
            return f"{PUBLIC_BASE_URL}/{file_id}.mp3"

        return None

    except Exception:
        return None
