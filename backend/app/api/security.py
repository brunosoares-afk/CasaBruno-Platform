import ipaddress
import secrets

from fastapi import Header, HTTPException, Request

from app.config.settings import settings


def require_api_key(x_api_key: str = Header(default="")):
    if not settings.API_KEY or not secrets.compare_digest(x_api_key, settings.API_KEY):
        raise HTTPException(status_code=401, detail="Invalid or missing API key")


# Rede do escritório onde este host físico roda (192.168.10.0/24). Não há
# nenhum uso legítimo vindo dela — o uso real do Fred vem de casa (via
# túnel wg-mikrotik), da tailnet do Bruno, ou do próprio host — mas como o
# backend escuta em 0.0.0.0 sem firewall próprio, qualquer colega/
# dispositivo dessa rede conseguia chamar /execute, /ask etc. direto,
# contornando o allowlist do WhatsApp. Ver auditoria de 2026-09-02.
# Bloqueio por rede em vez de exigir login: essas rotas são usadas pela
# página "Principal" (sem login, de propósito) a partir de casa.
_BLOCKED_NETWORKS = [ipaddress.ip_network("192.168.10.0/24")]


def block_untrusted_network(request: Request):
    client_host = request.client.host if request.client else None
    try:
        ip = ipaddress.ip_address(client_host)
    except (ValueError, TypeError):
        return True

    if any(ip in net for net in _BLOCKED_NETWORKS):
        raise HTTPException(
            status_code=403,
            detail="Fred não aceita esse comando vindo da rede do escritório",
        )
    return True
