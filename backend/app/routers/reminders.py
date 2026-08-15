from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.api.auth import require_gerencia_session
from app.services import memory_service

router = APIRouter(
    tags=["REMINDERS"],
    dependencies=[Depends(require_gerencia_session)]
)


# ======================================================
# MODELO
# ======================================================

class ReminderCreate(BaseModel):

    date: str
    name: str
    description: str | None = None


class ReminderUpdate(BaseModel):

    date: str | None = None
    name: str | None = None
    description: str | None = None


# ======================================================
# CRUD
# ======================================================

@router.get("/reminders")
def list_reminders():
    return {"items": memory_service.list_reminders()}


@router.post("/reminders")
def create_reminder(data: ReminderCreate):

    reminder_id = memory_service.add_reminder(
        date=data.date,
        name=data.name,
        description=data.description,
    )

    return {"id": reminder_id}


@router.put("/reminders/{reminder_id}")
def update_reminder(reminder_id: int, data: ReminderUpdate):

    updated = memory_service.update_reminder(
        reminder_id,
        date=data.date,
        name=data.name,
        description=data.description,
    )

    if updated is None:
        return {"success": False, "message": "Lembrete não encontrado."}

    return {"success": True}


@router.delete("/reminders/{reminder_id}")
def delete_reminder(reminder_id: int):

    memory_service.delete_reminder(reminder_id)

    return {"success": True}
