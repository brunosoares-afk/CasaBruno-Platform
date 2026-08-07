from fastapi import APIRouter
from app.services.docker_service import get_containers

router = APIRouter()

@router.get("/containers")
def containers():
    return get_containers()
