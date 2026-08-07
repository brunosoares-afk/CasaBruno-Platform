from fastapi import APIRouter

from app.core.storage.api import api

router = APIRouter(
    prefix="/api/storage",
    tags=["Storage"]
)


@router.get("/info")
def info():
    return api.info()


@router.get("/list")
def list_files():
    return api.list()


@router.get("/exists/{name}")
def exists(name: str):
    return api.exists(name)


@router.get("/read/{name}")
def read(name: str):
    return api.read(name)


@router.post("/write/{name}")
def write(name: str, data: dict):
    return api.write(name, data)


@router.delete("/delete/{name}")
def delete(name: str):
    return api.delete(name)
