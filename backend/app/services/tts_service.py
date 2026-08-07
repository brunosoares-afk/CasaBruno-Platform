import subprocess
import uuid
import os
import time
from pathlib import Path

VENV_PIPER = "/opt/CasaBruno-Platform/backend/venv/bin/piper"
MODEL_PATH = "/opt/CasaBruno-Platform/backend/tts_models/pt_BR-jeff-medium.onnx"
AUDIO_DIR = Path("/opt/CasaBruno-Platform/backend/tts_audio")
PUBLIC_BASE_URL = "https://hda08fx9s7v.sn.mynetname.net:8443/alexa/audio"

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
    """Gera audio MP3 (48kbps, 16000Hz) a partir de texto, usando Piper TTS.
    Retorna a URL publica do arquivo gerado."""

    _cleanup_old_files()

    file_id = uuid.uuid4().hex
    wav_path = f"/tmp/fred_tts_{file_id}.wav"
    mp3_path = str(AUDIO_DIR / f"{file_id}.mp3")

    try:
        subprocess.run(
            [VENV_PIPER, "--model", MODEL_PATH, "--output_file", wav_path],
            input=text,
            capture_output=True,
            text=True,
            timeout=20,
        )

        subprocess.run(
            [
                "ffmpeg", "-y",
                "-i", wav_path,
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

        if os.path.exists(wav_path):
            os.remove(wav_path)

        if os.path.exists(mp3_path):
            return f"{PUBLIC_BASE_URL}/{file_id}.mp3"

        return None

    except Exception:
        return None
