from fastapi import APIRouter, Depends
from app.api.auth import require_gerencia_session
from app.services.docker_service import get_containers

router = APIRouter(dependencies=[Depends(require_gerencia_session)])

@router.get("/containers")
def containers():
    return get_containers()
