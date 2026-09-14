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


# aioamazondevices só expõe set_device_volume (valor absoluto 0-100),
# sem leitura de volume atual pro alexa-bridge repassar pra cá — então
# "sobe"/"abaixa o volume" (intent_engine.match_media_service) não tem
# um valor real de referência pra ajustar. Aproximação: guardamos o
# último nível que A GENTE mandou por dispositivo (não o real, que pode
# ter sido mudado na mão/por voz desde então) e damos um passo fixo a
# partir dali — melhor que a falha total de antes (esses comandos batiam
# direto no HA morto e sempre voltavam "não consegui executar").
_VOLUME_STEP = 0.15
_DEFAULT_VOLUME = 0.4
_last_volume: dict[str, float] = {}


def _step_volume(entity_id: str, delta: float) -> float:
    current = _last_volume.get(entity_id, _DEFAULT_VOLUME)
    new_level = max(0.0, min(1.0, current + delta))
    _last_volume[entity_id] = new_level
    return new_level


def volume_up(entity_id: str) -> bool:
    return set_volume(entity_id, _step_volume(entity_id, _VOLUME_STEP))


def volume_down(entity_id: str) -> bool:
    return set_volume(entity_id, _step_volume(entity_id, -_VOLUME_STEP))


def media_command(entity_id: str, command: str) -> bool:
    return _post("/media", entity_id=entity_id, command=command)


def speak(entity_id: str, text: str) -> bool:
    return _post("/speak", entity_id=entity_id, text=text)
