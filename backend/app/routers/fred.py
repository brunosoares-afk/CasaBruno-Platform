from fastapi import APIRouter
from pydantic import BaseModel
from app.services.fred_service import fred

router = APIRouter(
    tags=["FRED"]
)


# ======================================================
# MODELO
# ======================================================

class FredCommand(BaseModel):

    command: str



# ======================================================
# HEALTH
# ======================================================

@router.get("/status")
def status():

    return {

        "online": True,

        "service":
        "FRED Core v3"

    }



# ======================================================
# EXECUÇÃO
# ======================================================

@router.post("/execute")
def execute(
    data: FredCommand
):


    result = fred.process(
        data.command
    )


    return result



# ======================================================
# CHAT ALIAS
# ======================================================

@router.post("/ask")
def ask(
    data: FredCommand
):


    return fred.ask(
        data.command
    )
