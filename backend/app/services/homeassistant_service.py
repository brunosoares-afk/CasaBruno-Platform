import logging

from app.core.homeassistant.client import ha_client
from app.services import detection_service, ha_websocket_service, tuya_service

logger = logging.getLogger(__name__)


def get_homeassistant_status():
    try:
        ha_client.states()
        return {"online": True}
    except Exception as e:
        return {"online": False, "error": str(e)}


def get_states():
    # Snapshot local (ha_websocket_service) em vez de bater na REST do HA
    # a cada chamada — é a mesma fonte que já alimenta o frontend, já
    # inclui os overrides locais (Tuya da Fase 2, detecção da Fase 1) que
    # a REST crua do HA não tem, e não depende de round-trip de rede.
    snapshot = ha_websocket_service.get_snapshot()
    if snapshot:
        return snapshot
    try:
        return ha_client.states()
    except Exception as exc:
        # HA Core está desligado de propósito desde 2026-08-16 — sem isso,
        # todo caller de get_states() (jobs do scheduler, etc.) explodia
        # com traceback completo de ConnectionRefusedError toda vez que o
        # snapshot local (que também depende do HA estar de pé) vinha vazio.
        logger.warning("HA indisponível e snapshot local vazio: %s", exc)
        return []


def get_recognized_person():
    # Direto no serviço de detecção facial (:8091), sem passar pelo HA —
    # o HA só fazia polling do mesmo endpoint e reexpunha como sensor.
    try:
        name = detection_service.recognized_person_name(detection_service.get_face_status())
        if name in (None, "Ninguém", "Desconhecido"):
            return "desconhecido"
        return name
    except Exception:
        return "desconhecido"


def get_config():
    return ha_client.get("/config")


def call_service(domain, service, entity_id):
    if tuya_service.is_managed(entity_id) and service in ("turn_on", "turn_off"):
        device_key = tuya_service.device_key_for(entity_id)
        ok = tuya_service.turn_on(device_key) if service == "turn_on" else tuya_service.turn_off(device_key)
        return {
            "success": ok,
            "domain": domain,
            "service": service,
            "entity_id": entity_id,
            "result": {"local": "tuya"},
        }

    # Import adiado só pra quebrar o ciclo (scenes_service importa esse
    # módulo pra acionar a lâmpada Tuya dentro das cenas).
    from app.services import scenes_service
    if scenes_service.is_managed(entity_id) and service == "turn_on":
        result = scenes_service.run(entity_id)
        return {
            "success": result.get("success", False),
            "domain": domain,
            "service": service,
            "entity_id": entity_id,
            "result": result,
        }

    try:
        result = ha_client.call_service(
            domain,
            service,
            {"entity_id": entity_id}
        )
        return {
            "success": True,
            "domain": domain,
            "service": service,
            "entity_id": entity_id,
            "result": result
        }
    except Exception as e:
        return {
            "success": False,
            "domain": domain,
            "service": service,
            "entity_id": entity_id,
            "error": str(e)
        }
