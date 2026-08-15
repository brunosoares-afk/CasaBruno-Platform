import asyncio
import shutil
import subprocess
import tempfile
import wave
from pathlib import Path

import requests
from wyoming.asr import Transcribe, Transcript
from wyoming.audio import wav_to_chunks
from wyoming.client import AsyncTcpClient

from app.core.homeassistant.client import ha_client

# O addon oficial core_whisper (app_core_whisper, porta 10300) trava com
# SIGILL nesta CPU (Intel Core i3 M350, sem AVX) em qualquer backend
# (faster-whisper/CTranslate2 e transformers/PyTorch testados, ambos
# travam). Usa nosso próprio servidor Wyoming (stt_server.py, mesma
# máquina) que chama sherpa-onnx corretamente em vez disso — ver
# memória casa-bruno-whisper-avx-crash.
WHISPER_HOST = "127.0.0.1"
WHISPER_PORT = 10301

# TTS via HA Cloud (Nabu Casa), mesma voz neural Azure já usada nos
# anúncios da Alexa (tts_service.py) — trocado a partir do Piper local
# (pt_BR-faber-medium) porque soava robótico demais comparado ao que o
# usuário queria (ver memória casa-bruno-custom-frontend-dashboard). Já
# é uma assinatura paga existente, sem custo extra, e a qualidade da voz
# neural é muito superior à do Piper.
DEFAULT_TTS_VOICE = "AntonioNeural"


def _run_ffmpeg(args: list) -> None:
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error"] + args,
        check=True,
        capture_output=True,
    )


async def transcribe(audio_bytes: bytes) -> str:
    """Áudio do WhatsApp (ogg/opus, etc.) -> texto via Whisper (Wyoming)."""

    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp) / "input.audio"
        wav_path = Path(tmp) / "input.wav"
        src.write_bytes(audio_bytes)

        _run_ffmpeg([
            "-i", str(src),
            "-ar", "16000", "-ac", "1", "-sample_fmt", "s16",
            str(wav_path),
        ])

        async with AsyncTcpClient(WHISPER_HOST, WHISPER_PORT) as client:
            await client.write_event(Transcribe(language="pt").event())

            with wave.open(str(wav_path), "rb") as wav_file:
                for event in wav_to_chunks(
                    wav_file, 1024, start_event=True, stop_event=True
                ):
                    await client.write_event(event.event())

            while True:
                event = await client.read_event()
                if event is None:
                    return ""
                if Transcript.is_type(event.type):
                    return Transcript.from_event(event).text.strip()


def _ha_cloud_tts_sync(text: str, voice: str) -> bytes:
    """Texto -> mp3 (bytes) via HA Cloud (mesmo endpoint /tts_get_url
    usado pelos anúncios da Alexa em tts_service.py)."""

    data = ha_client.post(
        "/tts_get_url",
        {
            "platform": "cloud",
            "message": text,
            "language": "pt-BR",
            "options": {"voice": voice},
        },
    )

    audio_path = data.get("path")
    if not audio_path:
        raise RuntimeError("HA Cloud não retornou áudio (sem 'path' na resposta)")

    protocol = "https" if ha_client.ssl else "http"
    audio_url = f"{protocol}://{ha_client.host}:{ha_client.port}{audio_path}"

    response = requests.get(audio_url, timeout=15)
    response.raise_for_status()
    return response.content


async def _ha_cloud_tts(text: str, voice: str) -> bytes:
    # ha_client/requests são síncronos — roda numa thread separada pra
    # não travar o event loop enquanto espera a rede (chamada sempre
    # feita com await, tanto do WhatsApp quanto do /speak do navegador).
    return await asyncio.to_thread(_ha_cloud_tts_sync, text, voice)


async def synthesize(text: str, voice: str | None = None) -> bytes:
    """Texto -> áudio ogg/opus (nota de voz do WhatsApp) via HA Cloud."""

    mp3_bytes = await _ha_cloud_tts(text, voice or DEFAULT_TTS_VOICE)

    tmp_dir = Path(tempfile.mkdtemp())
    try:
        mp3_path = tmp_dir / "in.mp3"
        ogg_path = tmp_dir / "out.ogg"
        mp3_path.write_bytes(mp3_bytes)

        _run_ffmpeg([
            "-i", str(mp3_path),
            "-c:a", "libopus", "-b:a", "32k", "-ar", "48000", "-ac", "1",
            str(ogg_path),
        ])

        return ogg_path.read_bytes()
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


async def synthesize_wav(text: str, voice: str | None = None) -> bytes:
    """Texto -> áudio wav (tocável direto no navegador) via HA Cloud."""

    mp3_bytes = await _ha_cloud_tts(text, voice or DEFAULT_TTS_VOICE)

    tmp_dir = Path(tempfile.mkdtemp())
    try:
        mp3_path = tmp_dir / "in.mp3"
        wav_path = tmp_dir / "out.wav"
        mp3_path.write_bytes(mp3_bytes)

        _run_ffmpeg([
            "-i", str(mp3_path),
            str(wav_path),
        ])

        return wav_path.read_bytes()
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)
