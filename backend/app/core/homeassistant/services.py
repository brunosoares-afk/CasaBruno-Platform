from app.core.homeassistant.client import ha_client
from app.core.logger.logger import logger
from app.core.events.event_manager import event_manager


class HomeAssistantServices:

    def list(self):
        return ha_client.services()

    def call(
        self,
        domain,
        service,
        data=None
    ):

        if data is None:
            data = {}

        result = ha_client.call_service(
            domain,
            service,
            data
        )

        logger.info(
            "homeassistant",
            f"{domain}.{service}"
        )

        event_manager.emit(
            "ha.service_called",
            {
                "domain": domain,
                "service": service,
                "data": data,
                "result": result,
            }
        )

        return result

    def turn_on(self, entity_id):

        return self.call(
            "homeassistant",
            "turn_on",
            {
                "entity_id": entity_id
            }
        )

    def turn_off(self, entity_id):

        return self.call(
            "homeassistant",
            "turn_off",
            {
                "entity_id": entity_id
            }
        )


services = HomeAssistantServices()
