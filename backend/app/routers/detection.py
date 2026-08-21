from fastapi import APIRouter, Depends, HTTPException

from app.api.auth import require_gerencia_session
from app.services import detection_service

router = APIRouter(
    prefix="/detection",
    tags=["Detection"],
    dependencies=[Depends(require_gerencia_session)]
)


@router.get("/people")
def people():
    try:
        return detection_service.list_enrolled_people()
    except Exception as e:
        raise HTTPException(502, f"Falha ao falar com o serviço de detecção: {e}")


@router.post("/enroll")
def enroll(name: str):
    try:
        return detection_service.enroll_capture(name)
    except Exception as e:
        raise HTTPException(502, f"Falha ao capturar rosto: {e}")


@router.post("/train")
def train():
    try:
        return detection_service.train_model()
    except Exception as e:
        raise HTTPException(502, f"Falha ao treinar o modelo: {e}")


@router.delete("/people/{name}")
def delete_person(name: str):
    try:
        return detection_service.delete_person(name)
    except Exception as e:
        raise HTTPException(502, f"Falha ao remover cadastro: {e}")
