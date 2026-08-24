from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.api.auth import require_gerencia_session
from app.services import trusted_plates_service

router = APIRouter(
    prefix="/plates",
    tags=["Plates"],
    dependencies=[Depends(require_gerencia_session)]
)


class PlateRequest(BaseModel):
    name: str
    plate: str


@router.get("")
def list_plates():
    return trusted_plates_service.list_plates()


@router.post("")
def add_plate(request: PlateRequest):
    try:
        return trusted_plates_service.add_plate(request.name, request.plate)
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.delete("/{plate}")
def remove_plate(plate: str):
    if not trusted_plates_service.remove_plate(plate):
        raise HTTPException(404, "placa não encontrada")
    return {"deleted": plate}
