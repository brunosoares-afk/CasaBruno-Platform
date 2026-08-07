from fastapi import APIRouter

from app.core.kernel.api import api

router = APIRouter(
    prefix="/api/kernel",
    tags=["Kernel"]
)


@router.get("/info")
def info():
    return api.info()


@router.get("/registry")
def registry():
    return api.registry()


@router.get("/services")
def services():
    return api.services()


@router.get("/plugins")
def plugins():
    return api.plugins()


@router.get("/events")
def events():
    return api.events()


@router.get("/scheduler")
def scheduler():
    return api.scheduler()


@router.get("/health")
def health():
    return api.health()
