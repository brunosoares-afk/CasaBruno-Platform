import io
import logging

import numpy as np
import soundfile as sf
from fastapi import FastAPI, Response
from pydantic import BaseModel
from kokoro import KPipeline

logging.getLogger("kokoro").setLevel(logging.WARNING)

app = FastAPI()

# Um pipeline por idioma usado, carregado uma vez e reaproveitado — cada
# chamada só troca o `voice` (pm_alex etc.), não recarrega o modelo. CPU
# sem AVX2 (AMD FX-4100) já deixa a síntese ~2.3x mais lenta que tempo
# real, então recarregar o modelo a cada request seria inviável.
_pipelines = {}


def _pipeline_for(lang_code: str) -> KPipeline:
    if lang_code not in _pipelines:
        _pipelines[lang_code] = KPipeline(lang_code=lang_code)
    return _pipelines[lang_code]


class SynthesizeRequest(BaseModel):
    text: str
    voice: str = "pm_alex"
    lang_code: str = "p"  # p = português


@app.post("/synthesize")
def synthesize(data: SynthesizeRequest):
    pipeline = _pipeline_for(data.lang_code)
    generator = pipeline(data.text, voice=data.voice)

    chunks = [audio for _, _, audio in generator]
    full = np.concatenate(chunks) if chunks else np.zeros(0, dtype=np.float32)

    buf = io.BytesIO()
    sf.write(buf, full, 24000, format="WAV")

    return Response(content=buf.getvalue(), media_type="audio/wav")


@app.get("/health")
def health():
    return {"ok": True, "pipelines_loaded": list(_pipelines.keys())}
