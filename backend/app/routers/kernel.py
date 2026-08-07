from fastapi import APIRouter

from app.core.kernel.kernel import kernel

router = APIRouter(
    prefix="/kernel",
    tags=["CBOS Kernel"]
)


@router.get("/status")
def status():

    return kernel.status()
