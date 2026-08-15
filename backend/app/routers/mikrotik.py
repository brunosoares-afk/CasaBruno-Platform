from fastapi import APIRouter, Depends

from app.api.auth import require_gerencia_session
from app.core.mikrotik.client import mikrotik_client

router = APIRouter(
    prefix="/mikrotik",
    tags=["MikroTik"],
    dependencies=[Depends(require_gerencia_session)]
)


@router.get("")
def root():
    return {
        "module": "MikroTik",
        "status": "online"
    }


@router.get("/status")
def status():
    try:
        identity = mikrotik_client.identity()
        return {
            "connected": True,
            "identity": identity.get("name", "")
        }
    except Exception as e:
        return {
            "connected": False,
            "error": str(e)
        }


@router.get("/resource")
def resource():
    try:
        return mikrotik_client.resource()
    except Exception as e:
        return {"error": str(e)}


@router.get("/interfaces")
def interfaces():
    try:
        return mikrotik_client.interfaces()
    except Exception as e:
        return {"error": str(e)}


@router.get("/leases")
def leases():
    try:
        return mikrotik_client.dhcp_leases()
    except Exception as e:
        return {"error": str(e)}
