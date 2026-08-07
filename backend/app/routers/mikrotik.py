from fastapi import APIRouter

from app.core.mikrotik.client import mikrotik_client

router = APIRouter(
    prefix="/mikrotik",
    tags=["MikroTik"]
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
