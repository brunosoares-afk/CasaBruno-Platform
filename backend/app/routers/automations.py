from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services import automations_service

router = APIRouter(prefix="/automations", tags=["Automations"])


class ToggleBody(BaseModel):
    enabled: bool


@router.get("")
def list_automations():
    return automations_service.list_automations()


@router.post("/{key}")
def set_automation(key: str, body: ToggleBody):
    try:
        automations_service.set_enabled(key, body.enabled)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error))

    return {"success": True, "key": key, "enabled": body.enabled}
