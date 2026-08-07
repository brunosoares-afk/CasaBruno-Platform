import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from app.core.events.api import api

api.emit(
    "mqtt.connected",
    {
        "broker": "Mosquitto"
    }
)

api.emit(
    "homeassistant.started",
    {
        "host": "192.168.15.10"
    }
)

print("=" * 60)
print(api.summary())

print("=" * 60)
print(api.all())

print("=" * 60)
print(api.last())

print("=" * 60)
print(api.process_last())

print("=" * 60)
print(api.last())

print("=" * 60)
print(api.count())

print("=" * 60)
print(api.clear())

print("=" * 60)
print(api.summary())
