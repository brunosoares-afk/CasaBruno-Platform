from fastapi import APIRouter
from pydantic import BaseModel
from app.services.fred_service import fred
from app.services import memory_service

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



# ======================================================
# MEMÓRIA
# ======================================================

@router.get("/memory/{person}")
def memory(person: str):

    profile = memory_service.get_profile(person)
    recent = memory_service.get_recent_turns(person, limit=20)

    return {
        "person": person,
        "summary": profile.get("summary"),
        "turn_count": profile.get("turn_count"),
        "recent": [{"role": role, "message": message} for role, message in recent],
    }
