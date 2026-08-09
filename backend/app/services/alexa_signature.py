"""Verificação de assinatura de requisições da Alexa Skills Kit.

Segue a especificação oficial da Amazon:
https://developer.amazon.com/en-US/docs/alexa/custom-skills/host-a-custom-skill-as-a-web-service.html

1. A URL do certificado (header SignatureCertChainUrl) precisa ser do
   próprio S3 da Amazon, no caminho esperado.
2. O certificado buscado nessa URL precisa estar dentro da validade e
   ter "echo-api.amazon.com" no Subject Alternative Name.
3. A assinatura (header Signature, RSA-SHA1 em base64) precisa bater
   com o corpo bruto da requisição, usando a chave pública do
   certificado.
4. O timestamp dentro do corpo precisa ser recente (evita replay).
"""

import base64
import time
from datetime import datetime, timezone
from urllib.parse import urlparse

import requests
from cryptography import x509
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

ECHO_API_SAN = "echo-api.amazon.com"
CERT_URL_HOST = "s3.amazonaws.com"
CERT_URL_PATH_PREFIX = "/echo.api/"
MAX_TIMESTAMP_SKEW_SECONDS = 150
CERT_CACHE_TTL_SECONDS = 3600

_cert_cache: dict[str, tuple[object, float]] = {}


def _validate_cert_url(cert_url: str) -> bool:
    parsed = urlparse(cert_url)

    if parsed.scheme.lower() != "https":
        return False
    if (parsed.hostname or "").lower() != CERT_URL_HOST:
        return False
    if parsed.port not in (None, 443):
        return False
    if not parsed.path.startswith(CERT_URL_PATH_PREFIX):
        return False

    return True


def _fetch_certificate(cert_url: str):
    cached = _cert_cache.get(cert_url)
    now = time.time()
    if cached and (now - cached[1]) < CERT_CACHE_TTL_SECONDS:
        return cached[0]

    response = requests.get(cert_url, timeout=10)
    response.raise_for_status()
    cert = x509.load_pem_x509_certificate(response.content, default_backend())

    _cert_cache[cert_url] = (cert, now)
    return cert


def _certificate_is_valid(cert) -> bool:
    now = datetime.now(timezone.utc)
    if not (cert.not_valid_before_utc <= now <= cert.not_valid_after_utc):
        return False

    try:
        san = cert.extensions.get_extension_for_class(x509.SubjectAlternativeName)
        names = san.value.get_values_for_type(x509.DNSName)
    except x509.ExtensionNotFound:
        return False

    return ECHO_API_SAN in names


def _verify_signature(raw_body: bytes, signature_b64: str, cert) -> bool:
    try:
        signature = base64.b64decode(signature_b64)
    except Exception:
        return False

    try:
        cert.public_key().verify(
            signature,
            raw_body,
            padding.PKCS1v15(),
            hashes.SHA1(),
        )
        return True
    except InvalidSignature:
        return False
    except Exception:
        return False


def _timestamp_is_fresh(body: dict) -> bool:
    timestamp_str = body.get("request", {}).get("timestamp")
    if not timestamp_str:
        return False

    try:
        request_time = datetime.strptime(
            timestamp_str, "%Y-%m-%dT%H:%M:%SZ"
        ).replace(tzinfo=timezone.utc)
    except ValueError:
        return False

    delta = abs((datetime.now(timezone.utc) - request_time).total_seconds())
    return delta <= MAX_TIMESTAMP_SKEW_SECONDS


def verify_alexa_request(
    raw_body: bytes,
    body: dict,
    signature_b64: str | None,
    cert_url: str | None,
) -> tuple[bool, str]:
    """Retorna (valido, motivo). motivo só importa pra log quando valido=False."""

    if not signature_b64 or not cert_url:
        return False, "cabeçalhos de assinatura ausentes"

    if not _validate_cert_url(cert_url):
        return False, "URL do certificado fora do padrão esperado"

    try:
        cert = _fetch_certificate(cert_url)
    except Exception as e:
        return False, f"falha ao buscar certificado: {e}"

    if not _certificate_is_valid(cert):
        return False, "certificado expirado ou sem SAN echo-api.amazon.com"

    if not _verify_signature(raw_body, signature_b64, cert):
        return False, "assinatura não bate com o corpo da requisição"

    if not _timestamp_is_fresh(body):
        return False, "timestamp fora da janela de 150s (possível replay)"

    return True, "ok"
