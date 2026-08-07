from fastapi import APIRouter

from app.core.config.api import api

router = APIRouter(
    prefix="/api/config",
    tags=["Config"]
)


@router.get("/info")
def info():
    return api.info()


@router.get("/all")
def all():
    return api.all()


@router.get("/{section}")
def get(section: str):
    return api.get(section)


@router.post("/{section}")
def set(section: str, data: dict):
    return api.set(section, data)


@router.post("/reload")
def reload():
    return api.reload()


@router.post("/save")
def save():
    return api.save()

