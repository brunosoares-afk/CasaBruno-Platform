from fastapi import APIRouter, BackgroundTasks, Depends, Response
from pydantic import BaseModel
from app.api.auth import require_gerencia_session
from app.api.security import block_untrusted_network, require_api_key
from app.core.config.config import config
from app.services.fred_service import fred
from app.services import memory_service, voice_service, notify_service
from app.services.fred_memory import memory as fred_memory
from app.services.llm_service import llm_service
from datetime import datetime

router = APIRouter(
    tags=["FRED"]
)

DEFAULT_FRED_CONFIG = {"wakeWords": ["jarvis", "fred"], "voice": "pt_BR-cadu-medium"}


# ======================================================
# MODELO
# ======================================================

class FredCommand(BaseModel):

    command: str
    channel: str | None = None


class SpeakRequest(BaseModel):

    text: str
    voice: str | None = None


class FredSettings(BaseModel):

    wakeWords: list[str] | None = None
    voice: str | None = None


class NotifyRequest(BaseModel):

    text: str



# ======================================================
# HEALTH
# ======================================================

@router.get("/status")
def status():

    return {

        "online": True,

        "service":
        "FRED Core v3"

    }



# ======================================================
# EXECUÇÃO
# ======================================================

@router.post("/execute", dependencies=[Depends(block_untrusted_network)])
def execute(
    data: FredCommand
):


    result = fred.process(
        data.command,
        channel=data.channel or "web"
    )


    return result



# ======================================================
# CHAT ALIAS
# ======================================================

@router.post("/ask", dependencies=[Depends(block_untrusted_network)])
def ask(
    data: FredCommand
):


    return fred.ask(
        data.command,
        channel=data.channel or "voice"
    )



# ======================================================
# VOZ (TTS pra tocar no navegador)
# ======================================================

@router.post("/speak")
async def speak(
    data: SpeakRequest
):

    wav_bytes = await voice_service.synthesize_wav(
        data.text,
        voice=data.voice,
    )

    return Response(
        content=wav_bytes,
        media_type="audio/wav",
    )


# ======================================================
# SAUDAÇÃO PERSONALIZADA (reconhecimento facial pela câmera web)
# ======================================================
# Público de propósito, mesmo motivo do /fred/config — a página onde
# isso é chamado (Principal) não tem login. Ver
# [[casa-bruno-profile-aware-greeting-2026-08-23]].

@router.get("/fred/greet/{person}")
def greet(person: str):
    return {"text": llm_service.greet(person)}



# ======================================================
# CONFIGURAÇÃO (voz + palavra de ativação)
# ======================================================
# Endpoint público de propósito — o Chat roda na página Principal (sem
# login), então precisa ler essa config sem depender da sessão da Gerência.
# A mesma seção "fred" do config.json também é editável via /api/config/fred
# (Gerência → Configurações), que exige login — as duas rotas leem/escrevem
# o mesmo dado, só a exposição pública é diferente.

@router.get("/fred/config")
def get_fred_config():
    return {**DEFAULT_FRED_CONFIG, **(config.get("fred") or {})}


@router.post("/fred/config", dependencies=[Depends(block_untrusted_network)])
def set_fred_config(data: FredSettings):
    current = {**DEFAULT_FRED_CONFIG, **(config.get("fred") or {})}
    if data.wakeWords is not None:
        current["wakeWords"] = data.wakeWords
    if data.voice is not None:
        current["voice"] = data.voice
    config.set("fred", current)
    return current



# ======================================================
# MEMÓRIA
# ======================================================

@router.get("/memory/{person}", dependencies=[Depends(block_untrusted_network)])
def memory(person: str):

    profile = memory_service.get_profile(person)
    recent = memory_service.get_recent_turns(person, limit=20)

    return {
        "person": person,
        "summary": profile.get("summary"),
        "turn_count": profile.get("turn_count"),
        "recent": [{"role": role, "message": message} for role, message in recent],
    }



# ======================================================
# ATIVIDADE (dashboard)
# ======================================================

@router.get("/activity", dependencies=[Depends(block_untrusted_network)])
def activity(limit: int = 10, hours: int = 24):

    return {
        "recent": memory_service.get_recent_activity(limit=limit),
        "stats": memory_service.get_activity_stats(hours=hours),
    }



# ======================================================
# NOTIFICAÇÃO PROATIVA
# ======================================================
# Gancho pra qualquer automação da HA (via rest_command) ou pro
# scheduler_service empurrar um aviso pro Fred falar por conta própria
# (WhatsApp, texto+voz) — não é resposta a nada. Mesmo mecanismo de
# X-Api-Key já usado pelos rest_command dos endpoints /android/*.

@router.post("/fred/notify", dependencies=[Depends(require_gerencia_session)])
async def notify(data: NotifyRequest):
    sent = await notify_service.notify(data.text)
    return {"success": sent}


# ======================================================
# ALERTA DE LINK (CCR1016)
# ======================================================
# Chamado pelo netwatch do CCR1016 (192.168.2.1) via /tool fetch — pelo
# túnel WireGuard (192.168.99.3, não a VLAN20-Sogra: o ARP direto do
# roteador pra 192.168.10.10 falha, achado em 2026-09-12) — na queda e na
# volta do link PPPoE com a operadora.
# Autenticado por X-Api-Key (não por sessão) porque quem chama é o
# roteador, não um navegador logado.
# A duração é calculada aqui (não no RouterOS, cuja aritmética de tempo é
# frágil) guardando o instante da queda no fred_memory.
# Na queda o roteador ainda alcança esse endpoint (é rota direta pelo
# túnel, não passa pelo PPPoE) mas o envio real do WhatsApp pode falhar
# mesmo assim, pois o bridge também depende do mesmo link caído pra falar
# com os servidores do WhatsApp — nesse caso o aviso de volta (evento
# "up", com a duração) é o que garante a notificação.

class LinkAlertRequest(BaseModel):

    event: str  # "down" ou "up"


@router.post("/fred/alert/link", dependencies=[Depends(require_api_key)])
async def alert_link(data: LinkAlertRequest, background_tasks: BackgroundTasks):
    now = datetime.now()

    if data.event == "down":
        fred_memory.remember(None, "link_down_since", now.isoformat())
        text = f"⚠️ A internet caiu às {now.strftime('%H:%M')}."
    else:
        since_raw = fred_memory.recall(None, "link_down_since")
        text = f"✅ A internet voltou às {now.strftime('%H:%M')}"
        try:
            since = datetime.fromisoformat(since_raw) if since_raw else None
            if since:
                dur_min = round((now - since).total_seconds() / 60)
                text += f" (ficou {dur_min} min fora)"
        except (TypeError, ValueError):
            pass
        text += "."
        fred_memory.forget(None, "link_down_since")

    # Dispara em background: o /tool fetch do RouterOS desiste antes dos ~10s+
    # que o notify_service leva (síntese de voz do Kokoro é lenta nesta CPU),
    # e reportaria "falha" mesmo quando a mensagem sai normalmente depois.
    background_tasks.add_task(notify_service.notify, text)
    return {"success": True, "queued": True}
