import logging

import requests

from app.core.android.wol import send_wol

logger = logging.getLogger("philips_tv_service")
logger.setLevel(logging.INFO)
if not logging.getLogger().handlers:
    logging.basicConfig(level=logging.INFO)

# TV Philips 50PUG6513/78 (Saphi OS), sala — API JointSpace v6, porta 1925,
# sem pareamento (pairing_type: none no /system, confirmado ao vivo
# 2026-08-16). IP fixado no MikroTik (lease *332, DHCP-STREAM) pro host
# nunca mudar. Sem lib async mantida pra JointSpace — é só REST simples,
# não precisa vendorizar nada (diferente do DVR-IP da câmera).
HOST = "192.168.20.96"
MAC = "F8:A2:D6:21:2A:B9"
BASE = f"http://{HOST}:1925/6"
TIMEOUT = 5

# A TV só responde no /system quando em standby profundo. Um WoL acorda a
# rede por poucos segundos — se "Quick Start"/"Wake on LAN" não estiver
# ligado nas configurações da própria TV (Configurações > Eco), o boot
# completo não acontece só com o pacote mágico. Confirmado ao vivo: dá pra
# ler /system e às vezes /powerstate nesse instante, mas POST costuma
# falhar por timeout. Ligar a TV manualmente uma vez e habilitar Quick
# Start resolve isso pra sempre — sem isso, power_on() só tem a chance
# de funcionar nesse instante curto de rede acordada.


def _get(path: str):
    r = requests.get(f"{BASE}{path}", timeout=TIMEOUT)
    r.raise_for_status()
    return r.json()


def _post(path: str, payload: dict):
    r = requests.post(f"{BASE}{path}", json=payload, timeout=TIMEOUT)
    r.raise_for_status()
    # Vários endpoints do JointSpace respondem 200 com corpo vazio ou não-JSON
    # pra ações (ex: powerstate) — status 2xx já é o sucesso, não precisa
    # decodificar nada pra saber que funcionou.
    try:
        return r.json()
    except ValueError:
        return {}


def get_power_state() -> str | None:
    try:
        return _get("/powerstate").get("powerstate")
    except Exception:
        return None


def power_on() -> bool:
    send_wol(MAC, HOST)
    send_wol(MAC, "192.168.20.255")
    try:
        _post("/powerstate", {"powerstate": "On"})
        return True
    except Exception:
        logger.warning("TV Philips não respondeu ao ligar — provável Quick Start/Wake on LAN desligado na TV")
        return False


def power_off() -> bool:
    try:
        _post("/powerstate", {"powerstate": "Standby"})
        return True
    except Exception:
        logger.exception("Falha ao desligar TV Philips")
        return False


def send_key(key: str) -> bool:
    """key: nomes JointSpace — VolumeUp, VolumeDown, Mute, Home, Back,
    PlayPause, Confirm, CursorUp/Down/Left/Right, etc."""
    try:
        _post("/input/key", {"key": key})
        return True
    except Exception:
        logger.exception("Falha ao enviar tecla pra TV Philips: %s", key)
        return False


def volume_up() -> bool:
    return send_key("VolumeUp")


def volume_down() -> bool:
    return send_key("VolumeDown")


def mute() -> bool:
    return send_key("Mute")
