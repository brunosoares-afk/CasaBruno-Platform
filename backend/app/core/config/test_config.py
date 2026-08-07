import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from app.core.config.config import config

print("=" * 60)
print(config.summary())

print("=" * 60)
print(config.get())

print("=" * 60)
print(config.get("application"))

print("=" * 60)
print(config.get("homeassistant.host"))

print("=" * 60)
config.set("application.version", "2.0.0")

print(config.get("application"))
