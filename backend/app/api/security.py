import secrets

from fastapi import Header, HTTPException

from app.config.settings import settings


def require_api_key(x_api_key: str = Header(default="")):
    if not settings.API_KEY or not secrets.compare_digest(x_api_key, settings.API_KEY):
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
