from app.core.homeassistant.client import HomeAssistantClient


class SystemService:

    def __init__(self):
        self.ha = HomeAssistantClient()

    async def cpu(self):

        cpu = self.ha.entity(
            "sensor.home_assistant_core_cpu_percent"
        )

        return {
            "cpu_percent": cpu["state"]
        }

    async def memory(self):

        memory = self.ha.entity(
            "sensor.home_assistant_core_memory_percent"
        )

        return {
            "memory_percent": memory["state"]
        }
