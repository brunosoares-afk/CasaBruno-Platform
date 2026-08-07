from fastapi import APIRouter

from app.core.services.manager import service_manager

router = APIRouter(
    prefix="/services",
    tags=["CBOS Services"]
)


@router.get("")
def services():

    return service_manager.list()


@router.get("/health")
def health():

    return service_manager.health()
