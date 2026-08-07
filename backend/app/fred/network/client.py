import subprocess

from app.core.base_service import BaseService


class NetworkService(BaseService):

    NAME = "network"

    def info(self):
        return {
            "gateway": "192.168.2.1",
            "dns": "8.8.8.8"
        }

    def status(self):
        return {
            "status": "online"
        }

    def health(self):
        return {
            "gateway": self.ping("192.168.2.1"),
            "google": self.ping("8.8.8.8")
        }

    def ping(self, host):

        try:
            subprocess.check_output(
                ["ping", "-c", "1", "-W", "1", host],
                stderr=subprocess.DEVNULL
            )
            return True

        except Exception:
            return False

    def execute(self, action=None, params=None):
        return {
            "success": False,
            "action": action
        }

    def config(self):
        return {}


network = NetworkService()
