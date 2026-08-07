import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from app.core.services.api import api

api.register(
    "homeassistant",
    "Home Assistant Core"
)

api.register(
    "mqtt",
    "Mosquitto Broker"
)

print("=" * 60)
print(api.summary())

print("=" * 60)
print(api.list())

print("=" * 60)
print(api.all())

print("=" * 60)
print(api.start("homeassistant"))

print("=" * 60)
print(api.get("homeassistant"))

print("=" * 60)
print(api.restart("homeassistant"))

print("=" * 60)
print(api.stop("homeassistant"))

print("=" * 60)
print(api.count())
