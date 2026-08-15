from app.core.homeassistant.client import ha_client
from app.core.logger.logger import logger
from app.core.events.event_manager import event_manager
from app.services import tuya_service, scenes_service


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

        entity_id = data.get("entity_id")

        if tuya_service.is_managed(entity_id) and service in ("turn_on", "turn_off"):
            device_key = tuya_service.device_key_for(entity_id)
            ok = tuya_service.turn_on(device_key) if service == "turn_on" else tuya_service.turn_off(device_key)
            result = {"success": ok, "local": "tuya"}
        elif scenes_service.is_managed(entity_id) and service == "turn_on":
            result = scenes_service.run(entity_id)
        else:
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
