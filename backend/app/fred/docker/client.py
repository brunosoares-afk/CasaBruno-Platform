import subprocess

from app.core.base_service import BaseService


class DockerService(BaseService):

    NAME = "docker"

    def info(self):
        return {
            "engine": "docker"
        }

    def status(self):
        return {
            "status": "online"
        }

    def health(self):
        return {
            "containers": len(self.containers())
        }

    def containers(self):
        try:
            out = subprocess.check_output(
                ["docker","ps","--format","{{.Names}}"],
                text=True
            )
            return out.strip().splitlines()
        except Exception:
            return []

    def execute(self, action=None, params=None):
        return {
            "success": False,
            "action": action
        }

    def config(self):
        return {}


docker = DockerService()
