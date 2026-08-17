import logging
import threading
import time

from app.core.android.manager import AndroidManager
from app.core.android import commands
from app.core.android.wol import send_wol
from app.core.homeassistant.client import ha_client
from app.integrations.tuya import infrared
from app.services import alexa_service, homeassistant_service, philips_tv_service
from app.routers.scenes import _run_scene_unitv, _run_scene_desenho_heitor

logger = logging.getLogger("scenes_service")
logger.setLevel(logging.INFO)
if not logging.getLogger().handlers:
    logging.basicConfig(level=logging.INFO)

# Porta dos 12 scripts "fred_*" + 11 "cena_*" que moravam em scripts.yaml —
# cada um só existia lá como wrapper fino (script -> rest_command -> HTTP ->
# nosso próprio backend), ou combinando esses wrappers com Tuya (Fase 2).
# Migrar aqui elimina o round-trip inteiro pra quem já era nosso, e reduz o
# resto pro mínimo que ainda depende de fato do HA (Alexa, DND da TV/Alexa).

manager = AndroidManager()


# ==========================================================
# COMANDOS INDIVIDUAIS (fred_*)
# ==========================================================

def _adb_result(result) -> dict:
    """commands.* devolve o CompletedProcess cru — subprocess.run não
    levanta exceção em código de saída != 0, então sem essa checagem
    (mesma que o /android/{device}/{command} original já fazia) um ADB
    offline (ex.: BTV13, porta 5555 cai sozinha depois de reboot) reportava
    'success: true' mesmo sem executar nada."""
    if result.returncode != 0:
        error = result.stderr.strip() or f"adb saiu com código {result.returncode}"
        return {"success": False, "error": error}
    return {"success": True}


def tv_power():
    return infrared.tv_power()


def projector_power():
    return _adb_result(commands.power(manager.host("projector")))


def projector_home():
    return _adb_result(commands.home(manager.host("projector")))


def projector_back():
    return _adb_result(commands.back(manager.host("projector")))


def btv13_power():
    return _adb_result(commands.power(manager.host("btv13")))


def btv13_home():
    return _adb_result(commands.home(manager.host("btv13")))


def btv13_back():
    return _adb_result(commands.back(manager.host("btv13")))


def btv13_wake():
    mac = manager.mac("btv13")
    ip = manager.host("btv13").split(":")[0]
    send_wol(mac, ip)
    return {"success": True, "mac": mac, "ip": ip}


def air_on():
    return infrared.air_on()


def air_off():
    return infrared.air_off()


def air_temp(temp=23):
    return infrared.air_temp(temp)


def tv_philips_power():
    return {"success": philips_tv_service.power_on()}


def tv_philips_power_off():
    return {"success": philips_tv_service.power_off()}


def tv_philips_volume_up():
    return {"success": philips_tv_service.volume_up()}


def tv_philips_volume_down():
    return {"success": philips_tv_service.volume_down()}


def tv_philips_mute():
    return {"success": philips_tv_service.mute()}


def scene_unitv():
    threading.Thread(target=_run_scene_unitv, daemon=True).start()


def scene_desenho_heitor():
    threading.Thread(target=_run_scene_desenho_heitor, daemon=True).start()


# ==========================================================
# DND da TV/Alexa — antes passava pelo HA (integração alexa_devices);
# desde a Fase 8 da remoção do HA fala direto com o alexa-bridge (a TV
# "Bruno's N65B" é 100% gerenciada pela Alexa, não é Samsung nativa —
# achado ao auditar, ver [[casa-bruno-voice-piper-migration-2026-08-16]]).
# ==========================================================

_DND_SWITCH_TO_ENTITY = {
    "switch.bruno_s_n65b_do_not_disturb": "media_player.bruno_s_n65b",
    "switch.alexa_taiane_do_not_disturb": "media_player.alexa_taiane",
}


def _ha_switch(entity_id: str, on: bool):
    media_entity = _DND_SWITCH_TO_ENTITY.get(entity_id)
    if media_entity:
        alexa_service.set_dnd(media_entity, on)
        return
    ha_client.call_service("switch", "turn_on" if on else "turn_off", {"entity_id": entity_id})


def _alexa_volume(level: float):
    alexa_service.set_volume("media_player.alexa_taiane", level)


def _lamp(on: bool):
    homeassistant_service.call_service("switch", "turn_on" if on else "turn_off", "switch.lampada_cozinha_switch_1")


# ==========================================================
# CENAS (cena_*) — mesma sequência de scripts.yaml, ações locais
# chamadas em processo em vez de HA -> rest_command -> HTTP
# ==========================================================

def cena_modo_cinema():
    projector_power()
    time.sleep(5)
    projector_home()
    _lamp(False)
    _ha_switch("switch.bruno_s_n65b_do_not_disturb", True)


def cena_boa_noite():
    air_off()
    _lamp(False)


def cena_bom_dia():
    _lamp(True)


def cena_saida_de_casa():
    air_off()
    _lamp(False)


def cena_conforto_ar():
    air_on()
    time.sleep(2)
    air_temp(23)


def cena_fim_de_cinema():
    projector_power()
    _lamp(True)
    _ha_switch("switch.bruno_s_n65b_do_not_disturb", False)


def cena_nao_perturbe():
    _ha_switch("switch.alexa_taiane_do_not_disturb", True)
    _ha_switch("switch.bruno_s_n65b_do_not_disturb", True)


def cena_assistir_tv():
    tv_power()
    _ha_switch("switch.bruno_s_n65b_do_not_disturb", True)


def cena_modo_btv13():
    tv_power()
    btv13_power()
    time.sleep(5)
    btv13_home()


def cena_silencio_total():
    _ha_switch("switch.alexa_taiane_do_not_disturb", True)
    _ha_switch("switch.bruno_s_n65b_do_not_disturb", True)
    _alexa_volume(0.05)


# ==========================================================
# INTERCEPTAÇÃO — mesmo padrão da Fase 2 (tuya_service.is_managed):
# entity_id do "script.*" já usado pelo frontend/Fred continua igual,
# só passa a ser executado local em vez de ir pro HA.
# Cenas com sequência (delay) rodam em thread — mesmo motivo do
# scenes.py original: não travar o worker do FastAPI por vários segundos.
# ==========================================================

_THREADED = {"cena_modo_cinema", "cena_conforto_ar", "cena_fim_de_cinema", "cena_modo_btv13"}

_SCRIPT_FUNCS = {
    "fred_tv_power": tv_power,
    "fred_projector_power": projector_power,
    "fred_projector_home": projector_home,
    "fred_projector_back": projector_back,
    "fred_btv13_power": btv13_power,
    "fred_btv13_wake": btv13_wake,
    "fred_btv13_home": btv13_home,
    "fred_btv13_back": btv13_back,
    "fred_air_on": air_on,
    "fred_air_off": air_off,
    "fred_tv_philips_power": tv_philips_power,
    "fred_tv_philips_power_off": tv_philips_power_off,
    "fred_tv_philips_volume_up": tv_philips_volume_up,
    "fred_tv_philips_volume_down": tv_philips_volume_down,
    "fred_tv_philips_mute": tv_philips_mute,
    "fred_scene_unitv": scene_unitv,
    "fred_scene_desenho_heitor": scene_desenho_heitor,
    "cena_modo_cinema": cena_modo_cinema,
    "cena_boa_noite": cena_boa_noite,
    "cena_bom_dia": cena_bom_dia,
    "cena_saida_de_casa": cena_saida_de_casa,
    "cena_conforto_ar": cena_conforto_ar,
    "cena_fim_de_cinema": cena_fim_de_cinema,
    "cena_nao_perturbe": cena_nao_perturbe,
    "cena_assistir_tv": cena_assistir_tv,
    "cena_modo_btv13": cena_modo_btv13,
    "cena_silencio_total": cena_silencio_total,
}

SCRIPT_ENTITY_IDS = {f"script.{name}" for name in _SCRIPT_FUNCS}

# Nomes amigáveis das 10 cenas "cena_*" pra grade da Início — a HA
# fornecia isso via friendly_name do entity_id (puro metadado de
# listagem, a execução já era 100% local desde a Fase 3). Sem HA pra
# perguntar mais (desligada de vez, Fase 10), vira lista estática própria
# — mesmos rótulos já usados em AutomacoesView.jsx pra ficar consistente.
CENA_LABELS = {
    "cena_modo_cinema": "Modo Cinema",
    "cena_fim_de_cinema": "Fim de Cinema",
    "cena_assistir_tv": "Assistir TV",
    "cena_modo_btv13": "Modo BTV13",
    "cena_bom_dia": "Bom Dia",
    "cena_boa_noite": "Boa Noite",
    "cena_saida_de_casa": "Saída de Casa",
    "cena_conforto_ar": "Conforto (Ar)",
    "cena_nao_perturbe": "Não Perturbe",
    "cena_silencio_total": "Silêncio Total",
}


def list_cenas() -> list[dict]:
    return [
        {"entity_id": f"script.{name}", "label": label}
        for name, label in CENA_LABELS.items()
    ]


def is_managed(entity_id: str) -> bool:
    return entity_id in SCRIPT_ENTITY_IDS


def run(entity_id: str):
    name = entity_id.split(".", 1)[1]
    func = _SCRIPT_FUNCS[name]

    if name in _THREADED:
        threading.Thread(target=func, daemon=True).start()
        return {"success": True, "async": True}

    try:
        result = func()
        if isinstance(result, dict) and "success" in result:
            return result
        return {"success": True}
    except Exception as e:
        logger.exception("Falha ao executar %s", entity_id)
        return {"success": False, "error": str(e)}
