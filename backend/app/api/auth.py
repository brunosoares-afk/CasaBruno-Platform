import hashlib
import secrets
import time

from fastapi import APIRouter, Depends, Header, HTTPException

from app.config.settings import settings
from app.core.config.config import config

router = APIRouter(
    prefix="/api/auth/gerencia",
    tags=["Auth"]
)

TOKEN_TTL_SECONDS = 24 * 60 * 60

# Token de sessão em memória — suficiente para um app de usuário único; cai
# ao reiniciar o backend, forçando novo login (aceitável nesse contexto).
_sessions = {}

# Lockout de tentativas de login — a senha da Gerência é um PIN curto, sem
# isso dava pra tentar força-bruta sem limite nenhum. Ver auditoria de
# 2026-09-02. Em memória, reseta ao reiniciar o backend (aceitável, mesmo
# raciocínio das sessões acima).
_failed_attempts = []
MAX_LOGIN_ATTEMPTS = 5
LOGIN_WINDOW_SECONDS = 15 * 60  # janela deslizante: também é o tempo efetivo de bloqueio


def _check_login_lockout():
    now = time.time()
    _failed_attempts[:] = [t for t in _failed_attempts if now - t < LOGIN_WINDOW_SECONDS]
    if len(_failed_attempts) >= MAX_LOGIN_ATTEMPTS:
        wait_min = LOGIN_WINDOW_SECONDS // 60
        raise HTTPException(
            status_code=429,
            detail=f"Muitas tentativas incorretas — aguarde até {wait_min} min e tente de novo",
        )


def _register_login_failure():
    _failed_attempts.append(time.time())


def _register_login_success():
    _failed_attempts.clear()


def _hash_password(password: str, salt: str) -> str:
    return hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 200_000).hex()


def _get_or_seed_auth():
    auth = config.get("gerencia_auth")
    if not auth or "salt" not in auth or "password_hash" not in auth:
        salt = secrets.token_hex(16)
        auth = {"salt": salt, "password_hash": _hash_password(settings.GERENCIA_DEFAULT_PASSWORD, salt)}
        config.set("gerencia_auth", auth)
    return auth


def _cleanup_sessions():
    now = time.time()
    for token in [t for t, expires_at in _sessions.items() if expires_at < now]:
        del _sessions[token]


def require_gerencia_session(authorization: str = Header(default=""), x_api_key: str = Header(default="")):
    # Duas formas de passar: sessão de navegador (login da Gerência) OU uma
    # chave de serviço fixa (CBOS_API_KEY no .env) — usada por chamadas
    # servidor-a-servidor que nunca fazem login, como os sensores REST e
    # rest_command do próprio Home Assistant (configuration.yaml) batendo
    # direto nessas rotas pra ler status de rede/mikrotik/adb e acionar
    # projetor/BTV13/ar-condicionado.
    if settings.API_KEY and secrets.compare_digest(x_api_key, settings.API_KEY):
        return True

    _cleanup_sessions()
    token = authorization[7:].strip() if authorization.startswith("Bearer ") else ""
    if not token or token not in _sessions:
        raise HTTPException(status_code=401, detail="Sessão inválida ou expirada")
    return True


@router.post("/login")
def login(data: dict):
    _check_login_lockout()

    password = data.get("password", "")
    auth = _get_or_seed_auth()
    candidate = _hash_password(password, auth["salt"])
    if not secrets.compare_digest(candidate, auth["password_hash"]):
        _register_login_failure()
        raise HTTPException(status_code=401, detail="Senha incorreta")

    _register_login_success()
    _cleanup_sessions()
    token = secrets.token_urlsafe(32)
    _sessions[token] = time.time() + TOKEN_TTL_SECONDS
    return {"token": token, "expires_in": TOKEN_TTL_SECONDS}


@router.get("/verify")
def verify(_: bool = Depends(require_gerencia_session)):
    return {"valid": True}
