from fastapi import APIRouter

from app.core.plugins.manager import plugin_manager

router = APIRouter(
    prefix="/plugins",
    tags=["CBOS Plugins"]
)


@router.get("")
def plugins():

    return plugin_manager.list()


@router.post("/enable/{name}")
def enable(name: str):

    plugin_manager.enable(name)

    return {

        "success": True,

        "plugin": name,

        "status": "enabled"

    }


@router.post("/disable/{name}")
def disable(name: str):

    plugin_manager.disable(name)

    return {

        "success": True,

        "plugin": name,

        "status": "disabled"

    }
