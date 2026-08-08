from fastapi import APIRouter, Depends

from app.api.security import require_api_key
from app.core.database.api import api


router = APIRouter(
    prefix="/api/database",
    tags=["Database"],
    dependencies=[Depends(require_api_key)]
)


@router.get("/info")
def info():
    return api.info()


@router.get("/tables")
def tables():
    return api.tables()


@router.post("/execute")
def execute(sql: str, params: list | None = None):
    return api.execute(sql, tuple(params or []))


@router.post("/query")
def query(sql: str, params: list | None = None):
    return api.query(sql, tuple(params or []))


@router.post("/value")
def value(sql: str, params: list | None = None):
    return api.value(sql, tuple(params or []))

