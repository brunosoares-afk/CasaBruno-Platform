from fastapi import APIRouter

from app.core.application.api import api

router = APIRouter(
    prefix="/api/application",
    tags=["Application"]
)


@router.get("/info")
def info():
    return api.info()


@router.post("/start")
def start():
    return api.start()


@router.post("/stop")
def stop():
    return api.stop()


@router.post("/restart")
def restart():
    return api.restart()


@router.get("/kernel")
def kernel():
    return api.kernel()
