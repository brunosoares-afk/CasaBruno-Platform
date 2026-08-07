from fastapi import APIRouter

from app.core.plugins.api import api


router = APIRouter(
    prefix="/api/plugins",
    tags=["Plugins"]
)


@router.get("/info")
def info():
    return api.summary()


@router.get("/list")
def list_plugins():
    return api.list()


@router.get("/all")
def all_plugins():
    return api.all()


@router.get("/get/{name}")
def get(name: str):
    return api.get(name)


@router.post("/register/{name}")
def register(name: str, description: str = ""):
    return api.register(name, description)


@router.post("/load/{name}")
def load(name: str):
    return api.load(name)


@router.post("/enable/{name}")
def enable(name: str):
    return api.enable(name)


@router.post("/disable/{name}")
def disable(name: str):
    return api.disable(name)


@router.post("/unload/{name}")
def unload(name: str):
    return api.unload(name)
