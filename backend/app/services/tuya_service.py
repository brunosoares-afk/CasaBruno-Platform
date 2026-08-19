import logging

import tinytuya

from app.core.config.config import config

logger = logging.getLogger("tuya_service")
logger.setLevel(logging.INFO)
if not logging.getLogger().handlers:
    logging.basicConfig(level=logging.INFO)

# Mapa fixo: entity_id do HA -> chave do dispositivo em config["tuya"]["devices"].
# A lâmpada da cozinha tem dois entity_id no HA pro mesmo dispositivo físico
# (switch.* real + light.* template que só espelha o switch) — o frontend usa
# os dois em telas diferentes (EquipamentosView vs InicioView), e o Fred
# (intent_engine, fuzzy match por texto) pode resolver pra qualquer um dos dois.
ENTITY_TO_DEVICE = {
    "switch.lampada_cozinha_switch_1": "lampada_cozinha",
    "light.lampada_cozinha": "lampada_cozinha",
    "switch.portao_casa_switch_1": "portao",
}

MANAGED_ENTITY_IDS = set(ENTITY_TO_DEVICE.keys())


def is_managed(entity_id: str) -> bool:
    return entity_id in ENTITY_TO_DEVICE


def device_key_for(entity_id: str) -> str | None:
    return ENTITY_TO_DEVICE.get(entity_id)


def _device(device_key: str) -> tinytuya.OutletDevice:
    cfg = config.get("tuya", {}).get("devices", {})[device_key]
    dev = tinytuya.OutletDevice(cfg["device_id"], cfg["ip"], cfg["local_key"])
    dev.set_version(cfg["version"])
    dev.set_socketTimeout(5)
    return dev


def get_status(device_key: str) -> bool | None:
    try:
        result = _device(device_key).status()
    except Exception:
        logger.warning("Falha de conexão ao ler status do Tuya local: %s", device_key, exc_info=False)
        return None

    dps = result.get("dps") if isinstance(result, dict) else None
    if not dps or "1" not in dps:
        logger.warning(
            "Resposta Tuya sem 'dps' pro dispositivo %s (resposta: %s)", device_key, result
        )
        return None

    return bool(dps["1"])


def turn_on(device_key: str) -> bool:
    try:
        _device(device_key).turn_on()
        return True
    except Exception:
        logger.exception("Falha ao ligar Tuya local: %s", device_key)
        return False


def turn_off(device_key: str) -> bool:
    try:
        _device(device_key).turn_off()
        return True
    except Exception:
        logger.exception("Falha ao desligar Tuya local: %s", device_key)
        return False
