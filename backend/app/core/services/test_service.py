import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from app.core.services.service import Service

svc = Service(
    "HomeAssistant",
    "Home Assistant Core"
)

print("=" * 60)
print(svc.status())

print("=" * 60)
print(svc.start())

print("=" * 60)
print(svc.restart())

print("=" * 60)
print(svc.stop())
