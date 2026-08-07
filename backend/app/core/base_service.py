from app.core.interfaces import IService


class BaseService(IService):

    NAME = "service"

    def info(self):
        return {
            "name": self.NAME
        }

    def status(self):
        return {
            "status": "online"
        }

    def health(self):
        return {
            "healthy": True
        }

    def execute(self, action=None, params=None):
        return {
            "success": False,
            "action": action,
            "params": params
        }

    def config(self):
        return {}
