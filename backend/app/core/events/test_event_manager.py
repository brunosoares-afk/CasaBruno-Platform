import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from app.core.events.event_manager import event_manager


def callback(data):
    print("CALLBACK:", data)


event_manager.subscribe("system.start", callback)

event_manager.emit("system.start", {"status": "online"})
event_manager.emit("docker.restart", {"container": "homeassistant"})
event_manager.emit("system.start", {"status": "offline"})

print("=" * 60)
print(event_manager.history())
print("=" * 60)
print(event_manager.stats())
print("=" * 60)
print(event_manager.listeners())
print("=" * 60)
print(event_manager.events())
print("=" * 60)

event_manager.clear()

print(event_manager.events())
