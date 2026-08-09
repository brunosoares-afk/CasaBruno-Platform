import subprocess
import uuid
import os
import time
from pathlib import Path

import requests

from app.core.homeassistant.client import ha_client

AUDIO_DIR = Path("/opt/CasaBruno-Platform/backend/tts_audio")
PUBLIC_BASE_URL = "https://hda08fx9s7v.sn.mynetname.net/alexa/audio"

TTS_PLATFORM = "cloud"
TTS_LANGUAGE = "pt-BR"
TTS_VOICE = "AntonioNeural"

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
    """Gera audio MP3 (48kbps, 16000Hz) a partir de texto, usando a voz
    Antônio do Home Assistant Cloud (Nabu Casa). Retorna a URL publica
    do arquivo gerado."""

    _cleanup_old_files()

    file_id = uuid.uuid4().hex
    raw_path = f"/tmp/fred_tts_{file_id}.mp3"
    mp3_path = str(AUDIO_DIR / f"{file_id}.mp3")

    try:
        data = ha_client.post(
            "/tts_get_url",
            {
                "platform": TTS_PLATFORM,
                "message": text,
                "language": TTS_LANGUAGE,
                "options": {"voice": TTS_VOICE},
            },
        )
        audio_path = data.get("path")
        if not audio_path:
            return None

        protocol = "https" if ha_client.ssl else "http"
        audio_url = f"{protocol}://{ha_client.host}:{ha_client.port}{audio_path}"

        audio_response = requests.get(audio_url, timeout=15)
        audio_response.raise_for_status()

        with open(raw_path, "wb") as f:
            f.write(audio_response.content)

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
