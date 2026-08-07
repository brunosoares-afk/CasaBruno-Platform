import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.core.registry2 import registry2


class ServiceManager2:

    def services(self):
        return registry2.list()

    def get(self, name):
        return registry2.get(name)

    def info(self, name):
        service = self.get(name)
        return None if service is None else service.info()

    def status(self, name):
        service = self.get(name)
        return None if service is None else service.status()

    def health(self, name):
        service = self.get(name)
        return None if service is None else service.health()

    def config(self, name):
        service = self.get(name)
        return None if service is None else service.config()

    def execute(self, name, action=None, params=None):
        service = self.get(name)
        return None if service is None else service.execute(action, params)

    def reload(self):
        return registry2.reload()


# Instância principal
service_manager2 = ServiceManager2()

# Compatibilidade com versões anteriores
manager2 = service_manager2
