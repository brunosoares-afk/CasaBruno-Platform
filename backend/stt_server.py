"""
Servidor Wyoming de STT usando sherpa-onnx direto, em substituição ao addon
core_whisper do HA — na CPU antiga (Intel Core i3 M350, sem AVX) o addon
travava com SIGILL tanto no backend faster-whisper/CTranslate2 quanto no
backend transformers/PyTorch. O backend sherpa (onnxruntime) não trava, mas
o addon tem um bug de seleção de API pra modelos Whisper (chama
from_transducer em vez de from_whisper). Este servidor chama a API certa
diretamente.

A troca de hardware de 2026-08-18 trouxe uma CPU com AVX (AMD FX-4100),
então o modelo "tiny" (escolhido só pra rodar em qualquer CPU) deu lugar ao
"base" — mesma arquitetura sherpa-onnx, só um checkpoint maior e mais
preciso, sem trade-off técnico agora que o AVX não é mais um limite.

Fala o protocolo Wyoming de verdade (asr.Transcribe/Transcript,
audio.AudioStart/AudioChunk/AudioStop, info.Describe/Info) — qualquer
cliente Wyoming (HA, backend do CasaBruno) pode usar sem saber que não é
o addon oficial.
"""

import asyncio
import logging

import numpy as np
import sherpa_onnx

from wyoming.asr import Transcribe, Transcript
from wyoming.audio import AudioChunk, AudioStart, AudioStop
from wyoming.event import Event
from wyoming.info import AsrModel, AsrProgram, Attribution, Describe, Info
from wyoming.server import AsyncEventHandler, AsyncServer

MODEL_DIR = "/opt/CasaBruno-Platform/backend/stt_models/sherpa-onnx-whisper-base"
HOST = "127.0.0.1"
PORT = 10301

logging.basicConfig(level=logging.INFO)
_LOGGER = logging.getLogger("fred-stt-server")

_LOGGER.info("Carregando modelo sherpa-onnx (whisper base int8)...")
_recognizer = sherpa_onnx.OfflineRecognizer.from_whisper(
    encoder=f"{MODEL_DIR}/base-encoder.int8.onnx",
    decoder=f"{MODEL_DIR}/base-decoder.int8.onnx",
    tokens=f"{MODEL_DIR}/base-tokens.txt",
    language="pt",
    task="transcribe",
    num_threads=2,
)
_LOGGER.info("Modelo carregado.")

_WYOMING_INFO = Info(
    asr=[
        AsrProgram(
            name="fred-sherpa-whisper",
            description="Whisper base via sherpa-onnx (CPU com AVX desde a troca de hardware de 2026-08-18)",
            attribution=Attribution(name="CasaBruno", url="https://github.com/k2-fsa/sherpa-onnx"),
            installed=True,
            version="1.0.0",
            models=[
                AsrModel(
                    name="base-int8",
                    description="Whisper base int8 (sherpa-onnx)",
                    attribution=Attribution(name="OpenAI", url="https://github.com/openai/whisper"),
                    installed=True,
                    languages=["pt"],
                    version="1.0.0",
                )
            ],
        )
    ]
)


def _transcribe(audio_bytes: bytes) -> str:
    samples = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32) / 32768.0
    stream = _recognizer.create_stream()
    stream.accept_waveform(16000, samples)
    _recognizer.decode_stream(stream)
    return stream.result.text.strip()


class SherpaEventHandler(AsyncEventHandler):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._audio_buffer = bytearray()

    async def handle_event(self, event: Event) -> bool:

        if Describe.is_type(event.type):
            await self.write_event(_WYOMING_INFO.event())
            return True

        if Transcribe.is_type(event.type):
            self._audio_buffer = bytearray()
            return True

        if AudioStart.is_type(event.type):
            self._audio_buffer = bytearray()
            return True

        if AudioChunk.is_type(event.type):
            self._audio_buffer.extend(AudioChunk.from_event(event).audio)
            return True

        if AudioStop.is_type(event.type):
            text = await asyncio.get_running_loop().run_in_executor(
                None, _transcribe, bytes(self._audio_buffer)
            )
            _LOGGER.info("Transcrito: %r", text)
            await self.write_event(Transcript(text=text).event())
            self._audio_buffer = bytearray()
            return True

        return True


async def main():
    server = AsyncServer.from_uri(f"tcp://{HOST}:{PORT}")
    _LOGGER.info("Servidor Wyoming STT (sherpa-onnx) escutando em %s:%s", HOST, PORT)
    await server.run(SherpaEventHandler)


if __name__ == "__main__":
    asyncio.run(main())
