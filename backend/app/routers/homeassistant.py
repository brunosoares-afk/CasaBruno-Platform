import requests
from fastapi import APIRouter, Response, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

from app.core.homeassistant.manager import homeassistant
from app.services import ha_websocket_service


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
    return homeassistant.states.all()


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


@router.get("/camera/{entity_id}")
def camera_proxy(entity_id: str):
    stream = GO2RTC_STREAM_BY_ENTITY.get(entity_id)

    if not stream:
        # Sem mapeamento conhecido — cai pro proxy do HA como antes,
        # em vez de simplesmente falhar pra qualquer câmera nova.
        r = homeassistant.client.get_raw(f"/camera_proxy/{entity_id}")
        return Response(
            content=r.content,
            status_code=r.status_code,
            media_type=r.headers.get("Content-Type", "image/jpeg"),
        )

    r = requests.get(f"{GO2RTC_URL}/api/frame.jpeg", params={"src": stream}, timeout=10)

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
