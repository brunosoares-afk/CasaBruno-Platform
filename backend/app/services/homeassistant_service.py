from app.core.homeassistant.client import ha_client


def get_homeassistant_status():
    try:
        ha_client.states()
        return {"online": True}
    except Exception as e:
        return {"online": False, "error": str(e)}


def get_states():
    return ha_client.states()


def get_recognized_person():
    try:
        data = ha_client.get("/states/sensor.icsee_pessoa_reconhecida")
        state = data.get("state")
        if state in (None, "Ninguém", "Desconhecido", "unavailable", "unknown"):
            return "desconhecido"
        return state
    except Exception:
        return "desconhecido"


def get_config():
    return ha_client.get("/config")


def call_service(domain, service, entity_id):
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
