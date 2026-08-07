from app.core.homeassistant.client import HomeAssistantClient


class NetworkService:

    def __init__(self):
        self.ha = HomeAssistantClient()

    async def devices(self):

        states = self.ha.states()

        devices = []

        for entity in states:

            if not entity["entity_id"].startswith(
                "device_tracker."
            ):
                continue

            devices.append(
                {
                    "name": entity["attributes"].get(
                        "friendly_name"
                    ),
                    "state": entity["state"]
                }
            )

        return devices
