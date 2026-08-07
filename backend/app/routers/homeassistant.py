from fastapi import APIRouter
from pydantic import BaseModel

from app.core.homeassistant.manager import homeassistant


router = APIRouter(
    prefix="/homeassistant",
    tags=["Home Assistant"]
)


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


@router.get("/weather")
def weather():
    return homeassistant.weather.current()


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
