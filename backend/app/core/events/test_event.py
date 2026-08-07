import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from app.core.events.event import Event

ev = Event(
    "device.connected",
    {
        "device": "sensor01",
        "ip": "192.168.2.10"
    }
)

print("=" * 60)
print(ev.status())

print("=" * 60)
print(ev.process())

print("=" * 60)
print(ev.status())
