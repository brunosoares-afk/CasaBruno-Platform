from app.core.homeassistant.states import states


class HomeAssistantWeather:

    def entities(self):

        return states.domain("weather")

    def current(self):

        weather = self.entities()

        if not weather:

            return {
                "online": False,
                "message": "Nenhuma entidade weather encontrada."
            }

        entity = weather[0]

        return {
            "entity_id": entity["entity_id"],
            "state": entity["state"],
            "attributes": entity.get("attributes", {})
        }

    def forecast(self):

        current = self.current()

        if not current.get("online", True):

            return current

        return current["attributes"].get("forecast", [])


weather = HomeAssistantWeather()
