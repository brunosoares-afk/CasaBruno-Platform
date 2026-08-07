import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from app.core.events.bus import event_bus


def callback(data):
    print("CALLBACK:", data)


event_bus.subscribe("system.start", callback)

event_bus.publish(
    "system.start",
    {
        "status": "online"
    }
)

event_bus.publish(
    "docker.restart",
    {
        "container": "homeassistant"
    }
)

print()

print(event_bus.events())

print()

print(event_bus.subscribers_list())
