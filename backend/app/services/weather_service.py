from app.services.homeassistant_service import get_states


WEATHER_ENTITY = "weather.forecast_casa"


def current():

    for entity in get_states():

        if entity["entity_id"] == WEATHER_ENTITY:

            attrs = entity.get("attributes", {})

            return {

                "clima": entity.get("state"),

                "temperatura": attrs.get("temperature"),

                "umidade": attrs.get("humidity"),

                "pressao": attrs.get("pressure"),

                "vento": attrs.get("wind_speed"),

                "direcao_vento": attrs.get("wind_bearing"),

                "visibilidade": attrs.get("visibility")

            }

    return {

        "error": "Clima indisponível"

    }


def summary():

    data = current()

    if "error" in data:

        return data

    return {

        "message": (
            f"Clima {data['clima']}, "
            f"{data['temperatura']}°C, "
            f"umidade {data['umidade']}%"
        )

    }
