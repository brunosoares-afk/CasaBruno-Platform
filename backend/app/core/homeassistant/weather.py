from app.services import weather_service


class HomeAssistantWeather:
    """Antes lia weather.forecast_casa direto do HA (states.domain), sem
    nenhum fallback — se o HA caísse, todo mundo que chamava isso caía
    junto. Agora usa a mesma API pública (Open-Meteo) que o frontend e o
    Fred (weather_service.py) já usam há tempos, então HA sair do ar
    de vez (Fase 11) não derruba isso."""

    def current(self):
        try:
            w = weather_service.get_current()
        except Exception:
            return {
                "online": False,
                "message": "Não consegui checar o clima agora."
            }

        return {
            "entity_id": "weather.forecast_casa",
            "state": w["label"],
            "attributes": {
                "temperature": w["temperature"],
                "feels_like": w["feels_like"],
                "humidity": w["humidity"],
                "wind_speed": w["wind_speed"],
                "friendly_name": "Forecast Casa",
            },
        }

    def forecast(self):
        try:
            return weather_service.get_forecast()
        except Exception:
            return []


weather = HomeAssistantWeather()
