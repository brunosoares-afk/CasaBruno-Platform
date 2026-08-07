from fastapi import APIRouter

from app.core.android.manager import AndroidManager
from app.core.android import commands

router = APIRouter(prefix="/android", tags=["Android"])

manager = AndroidManager()


@router.get("/devices")
def devices():
    return {"devices": manager.list()}


@router.get("/{device}/{command}")
def execute(device: str, command: str):

    if not hasattr(commands, command):
        return {"success": False}

    getattr(commands, command)(manager.host(device))

    return {"success": True}
