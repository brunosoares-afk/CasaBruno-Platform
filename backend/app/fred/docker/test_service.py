import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from fred.docker.client import docker

print(docker.info())
print(docker.status())
print(docker.health())
print(docker.containers())
print(docker.execute("restart"))
print(docker.config())
