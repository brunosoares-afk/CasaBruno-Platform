from fastapi import APIRouter

from app.core.android.manager import AndroidManager
from app.core.android import commands
from app.core.android.wol import send_wol

router = APIRouter(prefix="/android", tags=["Android"])

manager = AndroidManager()


@router.get("/devices")
def devices():
    return {"devices": manager.list()}


@router.post("/{device}/wake")
def wake(device: str):

    if device not in manager.devices:
        return {"success": False, "error": f"Dispositivo '{device}' não encontrado"}

    mac = manager.mac(device)

    if not mac:
        return {"success": False, "error": "Dispositivo sem MAC cadastrado para Wake-on-LAN"}

    ip = manager.host(device).split(":")[0]
    send_wol(mac, ip)

    return {"success": True, "mac": mac, "ip": ip}


@router.get("/{device}/{command}")
def execute(device: str, command: str):

    if device not in manager.devices:
        return {"success": False, "error": f"Dispositivo '{device}' não encontrado"}

    if not hasattr(commands, command):
        return {"success": False, "error": f"Comando '{command}' não existe"}

    result = getattr(commands, command)(manager.host(device))

    if result.returncode != 0:
        error = result.stderr.strip() or f"adb saiu com código {result.returncode}"
        return {"success": False, "error": error}

    return {"success": True}
