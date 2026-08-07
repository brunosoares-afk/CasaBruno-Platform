from app.services.device_service import get_entity
from app.services.weather_service import current as weather
from app.services.location_service import current as location


def house():

    lamp = get_entity("switch.lampada_cozinha_switch_1")
    gate = get_entity("switch.portao_casa_switch_1")
    battery = get_entity("sensor.2303era42l_battery_level")
    cpu = get_entity("sensor.home_assistant_core_cpu_percent")
    memory = get_entity("sensor.home_assistant_core_memory_percent")

    clima = weather()
    local = location()

    return {

        "clima": clima,

        "localizacao": local,

        "lampada_cozinha": lamp["state"] if lamp else "unknown",

        "portao": gate["state"] if gate else "unknown",

        "bateria_celular": battery["state"] if battery else None,

        "cpu_homeassistant": cpu["state"] if cpu else None,

        "memoria_homeassistant": memory["state"] if memory else None

    }


def summary():

    return house()
