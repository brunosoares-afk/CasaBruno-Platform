import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.core.registry import registry
from app.core.base_service import BaseService


class DockerService(BaseService):
    NAME = "docker"


class HomeAssistantService(BaseService):
    NAME = "homeassistant"


registry.register("docker", DockerService())
registry.register("homeassistant", HomeAssistantService())

for name in registry.list():

    service = registry.get(name)

    print(name)
    print(service.info())
    print(service.status())
    print(service.health())
    print("---")
