from app.core.homeassistant.client import ha_client


class HomeAssistantStates:

    def all(self):

        return ha_client.states()

    def entity(self, entity_id):

        return ha_client.entity(entity_id)

    def domain(self, domain):

        entities = self.all()

        return [

            entity

            for entity in entities

            if entity["entity_id"].startswith(f"{domain}.")

        ]

    def online(self):

        try:

            self.all()

            return True

        except Exception:

            return False


states = HomeAssistantStates()
