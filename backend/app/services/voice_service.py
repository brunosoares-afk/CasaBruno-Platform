import io
import shutil
import subprocess
import tempfile
import wave
from pathlib import Path

from wyoming.asr import Transcribe, Transcript
from wyoming.audio import AudioChunk, AudioStart, AudioStop, wav_to_chunks
from wyoming.client import AsyncTcpClient
from wyoming.tts import Synthesize, SynthesizeVoice

# O addon oficial core_whisper (app_core_whisper, porta 10300) trava com
# SIGILL nesta CPU (Intel Core i3 M350, sem AVX) em qualquer backend
# (faster-whisper/CTranslate2 e transformers/PyTorch testados, ambos
# travam). Usa nosso próprio servidor Wyoming (stt_server.py, mesma
# máquina) que chama sherpa-onnx corretamente em vez disso — ver
# memória casa-bruno-whisper-avx-crash.
WHISPER_HOST = "127.0.0.1"
WHISPER_PORT = 10301

# TTS via Piper local (container cbos-piper, Fase 6 da remoção do HA) —
# até 2026-08-16 isso ia pro HA Cloud (Nabu Casa, voz neural Azure); a
# qualidade era melhor, mas todo canal (WhatsApp, Jarvis, avisos
# proativos) dependia da HA pra falar. Trocado de volta pro Piper
# (achado "robótico demais" quando isso foi decidido antes, ver memória
# casa-bruno-custom-frontend-dashboard) como troca consciente de
# qualidade por independência — decisão do usuário, não peso técnico.
PIPER_HOST = "127.0.0.1"
PIPER_PORT = 10200
DEFAULT_TTS_VOICE = "pt_BR-faber-medium"


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


async def piper_tts(text: str, voice: str) -> bytes:
    """Texto -> wav (bytes) via nosso container Piper standalone (Wyoming,
    porta 10200, ver [[casa-bruno-ha-removal-phases-4-6]] Fase 6)."""

    async with AsyncTcpClient(PIPER_HOST, PIPER_PORT) as client:
        await client.write_event(
            Synthesize(text=text, voice=SynthesizeVoice(name=voice)).event()
        )

        wav_params = None
        pcm = bytearray()

        while True:
            event = await client.read_event()
            if event is None:
                break
            if AudioStart.is_type(event.type):
                start = AudioStart.from_event(event)
                wav_params = (start.rate, start.width, start.channels)
            elif AudioChunk.is_type(event.type):
                pcm.extend(AudioChunk.from_event(event).audio)
            elif AudioStop.is_type(event.type):
                break

    if wav_params is None:
        raise RuntimeError("Piper não retornou áudio")

    rate, width, channels = wav_params
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wav_file:
        wav_file.setnchannels(channels)
        wav_file.setsampwidth(width)
        wav_file.setframerate(rate)
        wav_file.writeframes(bytes(pcm))

    return buf.getvalue()


async def synthesize(text: str, voice: str | None = None) -> bytes:
    """Texto -> áudio ogg/opus (nota de voz do WhatsApp) via Piper local."""

    wav_bytes = await piper_tts(text, voice or DEFAULT_TTS_VOICE)

    tmp_dir = Path(tempfile.mkdtemp())
    try:
        wav_path = tmp_dir / "in.wav"
        ogg_path = tmp_dir / "out.ogg"
        wav_path.write_bytes(wav_bytes)

        _run_ffmpeg([
            "-i", str(wav_path),
            "-c:a", "libopus", "-b:a", "32k", "-ar", "48000", "-ac", "1",
            str(ogg_path),
        ])

        return ogg_path.read_bytes()
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


async def synthesize_wav(text: str, voice: str | None = None) -> bytes:
    """Texto -> áudio wav (tocável direto no navegador) via Piper local."""

    return await piper_tts(text, voice or DEFAULT_TTS_VOICE)
