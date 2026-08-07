import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from app.core.plugins.plugin import Plugin

plugin = Plugin(
    "mqtt",
    "Mosquitto MQTT Plugin"
)

print("=" * 60)
print(plugin.status())

print("=" * 60)
print(plugin.load())

print("=" * 60)
print(plugin.enable())

print("=" * 60)
print(plugin.disable())

print("=" * 60)
print(plugin.unload())
