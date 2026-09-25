import logging

import time
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


def _ler_status_uma_vez(device_key: str):
    try:
        result = _device(device_key).status()
    except Exception as e:  # noqa: BLE001
        return None, f"falha de conexão ({e})"
    dps = result.get("dps") if isinstance(result, dict) else None
    if not dps or "1" not in dps:
        return None, result
    return bool(dps["1"]), None


def get_status(device_key: str) -> bool | None:
    # Só LEITURA do estado — por isso pode repetir sem risco (nunca repete turn_on/turn_off, que
    # acionam o portão). 2026-09-25: o portão perde ~20% dos pacotes (Wi-Fi fraco onde ele fica),
    # então 1 tentativa a mais evita marcar "sem resposta" por um pacote perdido.
    estado, erro = _ler_status_uma_vez(device_key)
    if estado is None:
        time.sleep(1.5)
        estado, erro = _ler_status_uma_vez(device_key)
    if estado is None:
        logger.warning("Tuya %s sem resposta depois de 2 tentativas: %s", device_key, erro)
    return estado


def _send_ok(result) -> bool:
    """tinytuya não levanta exceção pra falhas de rede/protocolo (device
    unreachable, timeout etc) — devolve um dict com 'Error' em vez disso.
    Sem checar isso, turn_on/turn_off reportavam sucesso mesmo com o
    dispositivo totalmente fora do ar (descoberto 2026-08-20 investigando
    cenas que não faziam efeito nenhum mas sempre respondiam success)."""
    if isinstance(result, dict) and result.get("Error"):
        return False
    return True


def turn_on(device_key: str) -> bool:
    try:
        result = _device(device_key).turn_on()
        if not _send_ok(result):
            logger.warning("Tuya local não confirmou ligar %s: %s", device_key, result)
            return False
        return True
    except Exception:
        logger.exception("Falha ao ligar Tuya local: %s", device_key)
        return False


def turn_off(device_key: str) -> bool:
    try:
        result = _device(device_key).turn_off()
        if not _send_ok(result):
            logger.warning("Tuya local não confirmou desligar %s: %s", device_key, result)
            return False
        return True
    except Exception:
        logger.exception("Falha ao desligar Tuya local: %s", device_key)
        return False
