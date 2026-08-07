from fastapi import APIRouter

from app.core.events.api import api


router = APIRouter(
    prefix="/api/events",
    tags=["Events"]
)


@router.get("/info")
def info():
    return api.summary()


@router.get("/all")
def all_events():
    return api.all()


@router.get("/last")
def last():
    return api.last()


@router.get("/count")
def count():
    return api.count()


@router.post("/emit/{name}")
def emit(name: str):
    return api.emit(name)


@router.post("/emit_payload/{name}")
def emit_payload(name: str, payload: dict):
    return api.emit(name, payload)


@router.post("/process")
def process():
    return api.process_last()


@router.delete("/clear")
def clear():
    return api.clear()

