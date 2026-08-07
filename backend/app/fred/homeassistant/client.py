from app.core.base_service import BaseService


class HomeAssistantService(BaseService):

    NAME = "homeassistant"

    def __init__(self):
        self.host = "192.168.15.10"
        self.port = 8123

    def info(self):
        return {
            "host": self.host,
            "port": self.port
        }

    def status(self):
        return {
            "status": "online"
        }

    def health(self):
        return {
            "reachable": True
        }

    def execute(self, action=None, params=None):
        return {
            "success": False,
            "action": action
        }

    def config(self):
        return {
            "host": self.host,
            "port": self.port
        }


homeassistant = HomeAssistantService()
ha = homeassistant
