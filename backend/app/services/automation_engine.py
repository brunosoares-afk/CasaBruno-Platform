from app.services.homeassistant_service import (
    call_service,
    get_states,
)


class AutomationEngine:

    def execute(self, intent):

        if intent is None:
            return {
                "success": False,
                "message": "Não consegui entender o comando."
            }

        intent_type = intent.get("type")

        handlers = {
            "device_action": self._device_action,
            "device_status": self._device_status,
            "device_list": self._device_list,
            "domain_list": self._domain_list,
            "multiple_devices": self._multiple_devices,
            "device_not_found": self._device_not_found,
        }

        handler = handlers.get(intent_type)

        if handler:
            return handler(intent)

        return {
            "success": False,
            "message": f"Intent desconhecida: {intent_type}"
        }

    def _device_action(self, intent):

        entity_id = intent["entity_id"]

        domain = entity_id.split(".")[0]

        action = intent["action"]

        return call_service(
            domain,
            action,
            entity_id
        )

    def _device_status(self, intent):

        entity_id = intent["entity_id"]

        states = get_states()

        for entity in states:

            if entity["entity_id"] == entity_id:

                return {
                    "success": True,
                    "entity_id": entity_id,
                    "friendly_name": entity.get(
                        "attributes",
                        {}
                    ).get(
                        "friendly_name",
                        entity_id
                    ),
                    "state": entity.get("state"),
                    "attributes": entity.get("attributes", {})
                }

        return {
            "success": False,
            "message": "Dispositivo não encontrado."
        }

    def _device_list(self, intent):

        devices = intent.get("devices", [])

        return {
            "success": True,
            "count": len(devices),
            "devices": devices
        }

    def _domain_list(self, intent):

        devices = intent.get("devices", [])

        return {
            "success": True,
            "domain": intent.get("domain"),
            "count": len(devices),
            "devices": devices
        }

    def _multiple_devices(self, intent):

        return {
            "success": False,
            "message": "Foram encontrados vários dispositivos para este comando.",
            "count": len(intent.get("devices", [])),
            "devices": intent.get("devices", [])
        }

    def _device_not_found(self, intent):

        return {
            "success": False,
            "message": "Nenhum dispositivo encontrado.",
            "query": intent.get("query")
        }


automation_engine = AutomationEngine()
