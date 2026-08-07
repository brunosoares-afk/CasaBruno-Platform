import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.core.registry import registry

from system.system import system
from fred.docker.client import docker
from fred.homeassistant.client import homeassistant
from fred.network.client import network


registry.register(system.NAME, system)
registry.register(docker.NAME, docker)
registry.register(homeassistant.NAME, homeassistant)
registry.register(network.NAME, network)


if __name__ == "__main__":

    print(registry.list())

    for name in registry.list():

        service = registry.get(name)

        print(name)
        print(service.info())
