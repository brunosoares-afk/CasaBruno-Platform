from fastapi import APIRouter

from app.core.database.api import api


router = APIRouter(
    prefix="/api/database",
    tags=["Database"]
)


@router.get("/info")
def info():
    return api.info()


@router.get("/tables")
def tables():
    return api.tables()


@router.post("/execute")
def execute(sql: str, params: list = []):
    return api.execute(sql, tuple(params))


@router.post("/query")
def query(sql: str, params: list = []):
    return api.query(sql, tuple(params))


@router.post("/value")
def value(sql: str, params: list = []):
    return api.value(sql, tuple(params))

