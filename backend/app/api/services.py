from fastapi import APIRouter

from app.core.services.api import api


router = APIRouter(
    prefix="/api/services",
    tags=["Services"]
)


@router.get("/info")
def info():
    return {
        "version": api.VERSION,
        "services": api.count()
    }


@router.get("/list")
def list_services():
    return api.list()


@router.get("/all")
def all_services():
    return api.all()


@router.get("/get/{name}")
def get(name: str):
    return api.get(name)


@router.post("/register/{name}")
def register(name: str, description: str = ""):
    return api.register(name, description)


@router.post("/start/{name}")
def start(name: str):
    return api.start(name)


@router.post("/restart/{name}")
def restart(name: str):
    return api.restart(name)


@router.post("/stop/{name}")
def stop(name: str):
    return api.stop(name)

