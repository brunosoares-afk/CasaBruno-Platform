import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.core.discovery import discovery


class Registry2:

    def __init__(self):
        self.services = {}

    def load(self):
        self.services.clear()

        for service in discovery.discover():
            name = getattr(service, "NAME", service.__class__.__name__.lower())
            self.services[name] = service

    def list(self):
        return list(self.services.keys())

    def get(self, name):
        return self.services.get(name)

    def exists(self, name):
        return name in self.services

    def reload(self):
        self.load()
        return self.list()


registry2 = Registry2()
registry2.load()
