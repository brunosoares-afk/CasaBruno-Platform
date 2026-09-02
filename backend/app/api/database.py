from fastapi import APIRouter, Depends

from app.api.security import block_untrusted_network, require_api_key
from app.core.database.api import api


# SQL arbitrário direto no banco — protegido só pela CBOS_API_KEY, que
# também é usada por outras integrações (Android) e hoje não tem mais
# nenhum chamador real conhecido aqui (a HA que originalmente batia nessa
# rota foi desinstalada). Mantido funcional para debug manual, mas com uma
# camada a mais: bloqueia a rede do escritório mesmo com a chave certa.
# Ver auditoria de 2026-09-02.
router = APIRouter(
    prefix="/api/database",
    tags=["Database"],
    dependencies=[Depends(require_api_key), Depends(block_untrusted_network)]
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

