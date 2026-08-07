import platform
import psutil

from app.core.base_service import BaseService


class SystemService(BaseService):

    NAME = "system"

    def info(self):
        return {
            "hostname": platform.node(),
            "os": platform.system(),
            "release": platform.release()
        }

    def status(self):
        return {
            "status": "online"
        }

    def health(self):
        return {
            "cpu": psutil.cpu_percent(),
            "memory": psutil.virtual_memory().percent,
            "disk": round(psutil.disk_usage("/").percent,2)
        }

    def execute(self, action=None, params=None):
        return {
            "success": False,
            "message": "No executable actions"
        }

    def config(self):
        return {}

    def system_info(self):
        return {
            **self.info(),
            **self.health()
        }


system = SystemService()
