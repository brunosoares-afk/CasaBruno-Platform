import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from app.core.plugins.api import api

api.register(
    "mqtt",
    "Mosquitto Broker"
)

api.register(
    "homeassistant",
    "Home Assistant Integration"
)

print("=" * 60)
print(api.summary())

print("=" * 60)
print(api.list())

print("=" * 60)
print(api.all())

print("=" * 60)
print(api.load("mqtt"))

print("=" * 60)
print(api.enable("mqtt"))

print("=" * 60)
print(api.get("mqtt"))

print("=" * 60)
print(api.disable("mqtt"))

print("=" * 60)
print(api.unload("mqtt"))

print("=" * 60)
print(api.count())
