from fastapi import APIRouter

from app.core.bootstrap.api import api

router = APIRouter(
    prefix="/api/bootstrap",
    tags=["Bootstrap"]
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


@router.get("/discovery")
def discovery():
    return api.discovery()


@router.get("/services")
def services():
    return api.services()


@router.get("/plugins")
def plugins():
    return api.plugins()
