from app.core.homeassistant.states import states
from app.core.homeassistant.devices import devices
from app.core.homeassistant.services import services
from app.core.homeassistant.weather import weather
from app.core.homeassistant.client import ha_client
from app.core.homeassistant.registry import registry


class HomeAssistantManager:

    def __init__(self):
        self.client = ha_client
        self.states = states
        self.devices = devices
        self.services = services
        self.weather = weather
        self.registry = registry

    def status(self):
        try:
            self.client.states()
            return {
                "online": True
            }
        except Exception as e:
            return {
                "online": False,
                "error": str(e)
            }

    def summary(self):
        return {
            "status": self.status(),
            "devices": self.devices.summary(),
            "weather": self.weather.current()
        }


homeassistant = HomeAssistantManager()
