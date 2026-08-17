"""
Orquestrador standalone de voz por wake-word ("Hey Jarvis"), substituindo
o assist_pipeline do HA Core (desligado 2026-08-16, ver
[[casa-bruno-ha-removal-phases-4-6]]).

Reimplementa localmente o papel que a HA fazia: recebe um stream contínuo
de áudio cru de um satélite (celular, Raspberry Pi, ESPHome — nenhum
existe ainda, ver [[casa-bruno-audit-2026-08-17]]), encaminha pro
cbos-openwakeword pra detectar a wake word, grava a janela de comando
que segue a detecção, manda pro cbos-stt, passa o texto pro Fred (o
mesmo `fred.ask` que WhatsApp já usa) e devolve a resposta em áudio via
Piper.

Protocolo esperado do satélite: um único `AudioStart` (rate/width/
channels do mic) seguido de `AudioChunk`s contínuos enquanto o
dispositivo estiver com o microfone aberto — não há "turnos" no lado do
satélite, quem decide quando gravar um comando é este servidor, ao
detectar a wake word. Sem VAD ainda: a janela de comando tem duração
fixa (COMMAND_WINDOW_S) em vez de terminar no silêncio — suficiente pra
um MVP, mas o primeiro upgrade natural quando houver hardware real pra
testar contra.
"""

import asyncio
import io
import logging
import wave

from wyoming.audio import AudioChunk, AudioFormat, AudioStart, AudioStop
from wyoming.client import AsyncTcpClient
from wyoming.event import Event
from wyoming.server import AsyncEventHandler, AsyncTcpServer
from wyoming.wake import Detection

from app.services import voice_service
from app.services.fred_service import fred

logger = logging.getLogger("voice_satellite_service")

HOST = "0.0.0.0"
PORT = 10500

WAKE_HOST = "127.0.0.1"
WAKE_PORT = 10400

# Sem STT dedicado a essa janela ainda: usa o mesmo Whisper Wyoming local
# (voice_service.transcribe) que o WhatsApp já usa pra notas de voz.
LLM_TIMEOUT = 180  # mesmo valor de app/routers/whatsapp.py — Ollama sem AVX é lento

COMMAND_WINDOW_S = 6.0
CHUNK_SEND_BYTES = 2048


def _pcm_to_wav(pcm_bytes: bytes, fmt: AudioFormat) -> bytes:
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wav_file:
        wav_file.setnchannels(fmt.channels)
        wav_file.setsampwidth(fmt.width)
        wav_file.setframerate(fmt.rate)
        wav_file.writeframes(pcm_bytes)
    return buf.getvalue()


async def run_voice_turn(pcm_bytes: bytes, fmt: AudioFormat) -> bytes:
    """Áudio cru (pós wake-word) -> texto (STT) -> Fred -> áudio de resposta (TTS).

    Função isolada de propósito: é o único pedaço deste pipeline
    testável de ponta a ponta sem um satélite físico — dá pra alimentar
    com áudio sintético (ex: a própria saída do Piper) e verificar STT+
    Fred+TTS reais, mesmo sem a wake word em si.
    """

    wav_bytes = _pcm_to_wav(pcm_bytes, fmt)
    text = (await voice_service.transcribe(wav_bytes)).strip()

    if not text:
        logger.info("Comando de voz vazio após a wake word (nada transcrito)")
        return await voice_service.piper_tts(
            "Não entendi, pode repetir?", voice_service.DEFAULT_TTS_VOICE
        )

    logger.info("Comando de voz transcrito: %r", text)
    result = await asyncio.to_thread(fred.ask, text, LLM_TIMEOUT, "voice", None)
    message = result.get("message") or "Não consegui pensar em uma resposta."

    return await voice_service.piper_tts(message, voice_service.DEFAULT_TTS_VOICE)


class SatelliteHandler(AsyncEventHandler):
    def __init__(self, reader, writer):
        super().__init__(reader, writer)
        self._mic_format: AudioFormat | None = None
        self._state = "idle"  # idle -> listening -> recording -> listening
        self._wake_client: AsyncTcpClient | None = None
        self._wake_task: asyncio.Task | None = None
        self._command_chunks: list[bytes] = []
        self._command_deadline: float = 0.0

    async def handle_event(self, event: Event) -> bool:
        if AudioStart.is_type(event.type):
            start = AudioStart.from_event(event)
            self._mic_format = AudioFormat(
                rate=start.rate, width=start.width, channels=start.channels
            )
            await self._ensure_wake_client()
            self._state = "listening"
            return True

        if AudioChunk.is_type(event.type):
            await self._on_audio_chunk(AudioChunk.from_event(event))
            return True

        if AudioStop.is_type(event.type):
            if self._state == "recording" and self._command_chunks:
                await self._finish_command()
            self._state = "idle"
            return True

        return True

    async def _on_audio_chunk(self, chunk: AudioChunk) -> None:
        if self._state == "listening" and self._wake_client is not None:
            try:
                await self._wake_client.write_event(chunk.event())
            except Exception:
                logger.exception("Falha ao encaminhar áudio pro openwakeword")
        elif self._state == "recording":
            self._command_chunks.append(chunk.audio)
            if asyncio.get_event_loop().time() >= self._command_deadline:
                await self._finish_command()

    async def _ensure_wake_client(self) -> None:
        if self._wake_client is not None or self._mic_format is None:
            return

        self._wake_client = AsyncTcpClient(WAKE_HOST, WAKE_PORT)
        await self._wake_client.connect()
        await self._wake_client.write_event(
            AudioStart(
                rate=self._mic_format.rate,
                width=self._mic_format.width,
                channels=self._mic_format.channels,
            ).event()
        )
        self._wake_task = asyncio.create_task(self._listen_for_wake())

    async def _listen_for_wake(self) -> None:
        try:
            while True:
                event = await self._wake_client.read_event()
                if event is None:
                    break
                if Detection.is_type(event.type):
                    logger.info("Wake word detectada, gravando comando")
                    self._start_recording()
        except Exception:
            logger.exception("Conexão com o cbos-openwakeword caiu")

    def _start_recording(self) -> None:
        self._state = "recording"
        self._command_chunks = []
        self._command_deadline = asyncio.get_event_loop().time() + COMMAND_WINDOW_S

    async def _finish_command(self) -> None:
        self._state = "listening"
        pcm_bytes = b"".join(self._command_chunks)
        self._command_chunks = []

        if not pcm_bytes or self._mic_format is None:
            return

        try:
            reply_wav = await run_voice_turn(pcm_bytes, self._mic_format)
            await self._send_reply_audio(reply_wav)
        except Exception:
            logger.exception("Falha ao processar comando de voz do satélite")

    async def _send_reply_audio(self, wav_bytes: bytes) -> None:
        with wave.open(io.BytesIO(wav_bytes), "rb") as wf:
            fmt = AudioFormat(
                rate=wf.getframerate(), width=wf.getsampwidth(), channels=wf.getnchannels()
            )
            pcm = wf.readframes(wf.getnframes())

        await self.write_event(
            AudioStart(rate=fmt.rate, width=fmt.width, channels=fmt.channels).event()
        )
        for i in range(0, len(pcm), CHUNK_SEND_BYTES):
            await self.write_event(
                AudioChunk(
                    audio=pcm[i : i + CHUNK_SEND_BYTES],
                    rate=fmt.rate,
                    width=fmt.width,
                    channels=fmt.channels,
                ).event()
            )
        await self.write_event(AudioStop().event())

    async def disconnect(self) -> None:
        if self._wake_task is not None:
            self._wake_task.cancel()
        if self._wake_client is not None:
            try:
                await self._wake_client.disconnect()
            except Exception:
                pass


_server: AsyncTcpServer | None = None


def start_voice_satellite_server() -> None:
    global _server
    _server = AsyncTcpServer(HOST, PORT)
    asyncio.create_task(_server.run(SatelliteHandler))
    logger.info("Servidor de satélite de voz (wake-word) ouvindo em %s:%d", HOST, PORT)
