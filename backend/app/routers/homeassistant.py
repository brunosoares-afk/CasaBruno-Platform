import requests
from fastapi import APIRouter, Response, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

from app.core.homeassistant.manager import homeassistant
from app.services import ha_websocket_service, homeassistant_service, scenes_service


router = APIRouter(
    prefix="/homeassistant",
    tags=["Home Assistant"]
)

# entity_id do HA -> nome do stream real no go2rtc (mesmo mapeamento que
# o HA usava internamente pra fazer o proxy dessas câmeras — falado
# direto agora, sem passar pelo camera_proxy do HA).
GO2RTC_STREAM_BY_ENTITY = {
    "camera.camera_icsee_frente": "camera_frente",
    "camera.192_168_2_80": "camera_fundo_webrtc",
}
GO2RTC_URL = "http://127.0.0.1:1984"


class ServiceRequest(BaseModel):
    domain: str
    service: str
    data: dict = {}


@router.get("")
def root():
    return homeassistant.summary()


@router.get("/status")
def status():
    return homeassistant.status()


@router.get("/summary")
def summary():
    return homeassistant.summary()


@router.get("/states")
def states():
    # homeassistant.states.all() batia direto na REST crua da HA (sem
    # fallback) — desde que a HA foi desligada de vez (Fase 10) isso só
    # dava ConnectionError. homeassistant_service.get_states() já usa o
    # snapshot do relay (com os sintéticos) e só cai pra HA se o snapshot
    # estiver vazio, então sobrevive à HA estar fora do ar.
    return homeassistant_service.get_states()


@router.websocket("/ws")
async def states_ws(websocket: WebSocket):
    await websocket.accept()
    ha_websocket_service.register_client(websocket)
    try:
        await websocket.send_json({"type": "snapshot", "states": ha_websocket_service.get_snapshot()})
        while True:
            # Não esperamos nada do cliente — só mantém a conexão viva e
            # detecta desconexão. Recebe (e ignora) qualquer coisa que o
            # navegador mande, incluindo pings do próprio protocolo.
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        ha_websocket_service.unregister_client(websocket)


@router.get("/weather")
def weather():
    return homeassistant.weather.current()


@router.get("/areas")
def areas():
    return homeassistant.registry.areas_with_entities()


@router.get("/scenes")
def scenes():
    return scenes_service.list_cenas()


@router.get("/camera/{entity_id}")
def camera_proxy(entity_id: str):
    stream = GO2RTC_STREAM_BY_ENTITY.get(entity_id)

    if not stream:
        # Sem mapeamento conhecido — cai pro proxy do HA como antes,
        # em vez de simplesmente falhar pra qualquer câmera nova. HA não
        # existe mais, então isso sempre levanta ConnectionError agora —
        # 404 em vez de 500 sem corpo.
        try:
            r = homeassistant.client.get_raw(f"/camera_proxy/{entity_id}")
        except Exception:
            return Response(status_code=404)
        return Response(
            content=r.content,
            status_code=r.status_code,
            media_type=r.headers.get("Content-Type", "image/jpeg"),
        )

    # A câmera_fundo (Yoosee, UDP-only — ver [[casa-bruno-plate-detect-fix-2026-08-17]])
    # é consistentemente lenta pro go2rtc extrair um frame via WebRTC —
    # medido entre 10s e 17s em uso normal, não é falha passageira. O
    # timeout de 10s daqui vinha estourando quase toda chamada, e sem
    # try/except isso virava 500 puro pro frontend, que mostrava "Câmera
    # indisponível" mesmo com a câmera 100% online. 20s cobre o pior caso
    # observado; 404 em vez de 500 se mesmo assim estourar.
    try:
        r = requests.get(f"{GO2RTC_URL}/api/frame.jpeg", params={"src": stream}, timeout=20)
    except Exception:
        return Response(status_code=404)

    return Response(
        content=r.content,
        status_code=r.status_code,
        media_type=r.headers.get("Content-Type", "image/jpeg"),
    )


@router.get("/entity_picture/{entity_id}")
def entity_picture_proxy(entity_id: str):
    """Proxy pra attributes.entity_picture (capa do álbum etc) de qualquer
    entidade — o path que o HA manda (ex: /api/media_player_proxy/...) só
    é alcançável com o token de auth, o browser não pode buscar direto."""
    snapshot = {s["entity_id"]: s for s in ha_websocket_service.get_snapshot()}
    entity = snapshot.get(entity_id)
    picture_path = entity.get("attributes", {}).get("entity_picture") if entity else None

    if not picture_path:
        return Response(status_code=404)

    protocol = "https" if homeassistant.client.ssl else "http"
    url = f"{protocol}://{homeassistant.client.host}:{homeassistant.client.port}{picture_path}"
    try:
        r = requests.get(url, headers=homeassistant.client.headers(), timeout=10)
    except Exception:
        return Response(status_code=404)

    return Response(
        content=r.content,
        status_code=r.status_code,
        media_type=r.headers.get("Content-Type", "image/jpeg"),
    )


@router.get("/devices")
def devices():
    return homeassistant.devices.all()


@router.get("/devices/summary")
def devices_summary():
    return homeassistant.devices.summary()


@router.get("/services")
def services():
    return homeassistant.services.list()


@router.post("/service")
def service(request: ServiceRequest):
    return homeassistant.services.call(
        request.domain,
        request.service,
        request.data
    )
