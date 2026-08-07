import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.core.registry import registry
import app.core.register_services


class ServiceManager:

    def services(self):
        return registry.list()

    def info(self, name):
        service = registry.get(name)
        return None if service is None else service.info()

    def status(self, name):
        service = registry.get(name)
        return None if service is None else service.status()

    def health(self, name):
        service = registry.get(name)
        return None if service is None else service.health()

    def execute(self, name, action=None, params=None):
        service = registry.get(name)

        if service is None:
            return {"error": "service not found"}

        return service.execute(action, params)


manager = ServiceManager()
