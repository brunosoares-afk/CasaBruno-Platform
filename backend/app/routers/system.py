from fastapi import APIRouter

from app.services.system import get_system_status

router = APIRouter()


@router.get("/status")
def status():
    return get_system_status()
