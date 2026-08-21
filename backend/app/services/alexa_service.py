import logging

import requests

logger = logging.getLogger("alexa_service")
logger.setLevel(logging.INFO)
if not logging.getLogger().handlers:
    logging.basicConfig(level=logging.INFO)

# Container isolado (Python 3.12+, a lib aioamazondevices não roda no
# 3.11 do nosso venv) — ver [[casa-bruno-ha-removal-phases-4-6]] pro
# porquê e alexa-bridge/ na raiz do repo pro código do bridge em si.
BRIDGE_URL = "http://127.0.0.1:8097"
TIMEOUT = 15

MANAGED_ENTITY_IDS = {"media_player.alexa_taiane", "media_player.bruno_s_n65b"}


def is_managed(entity_id: str) -> bool:
    return entity_id in MANAGED_ENTITY_IDS


def devices() -> dict:
    """{serial: {name, online}} pros dispositivos Alexa — usado pelo
    loop nativo em ha_websocket_service.py pra alimentar
    media_player.alexa_taiane/bruno_s_n65b, que não existem mais desde
    que a HA saiu (nada mais os produzia, ficavam sempre '—' no
    dashboard)."""
    try:
        r = requests.get(f"{BRIDGE_URL}/devices", timeout=TIMEOUT)
        r.raise_for_status()
        return r.json()
    except Exception:
        logger.exception("Falha ao ler devices do alexa-bridge")
        return {}


def _post(path: str, **params) -> bool:
    try:
        r = requests.post(f"{BRIDGE_URL}{path}", params=params, timeout=TIMEOUT)
        r.raise_for_status()
        return True
    except Exception:
        logger.exception("Falha ao chamar alexa-bridge: %s %s", path, params)
        return False


def set_dnd(entity_id: str, enable: bool) -> bool:
    return _post("/dnd", entity_id=entity_id, enable=enable)


def set_volume(entity_id: str, level: float) -> bool:
    return _post("/volume", entity_id=entity_id, level=level)


def media_command(entity_id: str, command: str) -> bool:
    return _post("/media", entity_id=entity_id, command=command)


def speak(entity_id: str, text: str) -> bool:
    return _post("/speak", entity_id=entity_id, text=text)
