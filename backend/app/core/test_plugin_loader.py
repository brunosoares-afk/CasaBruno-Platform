import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.core.plugin_manager import plugin_manager
from app.core.plugin_loader import plugin_loader


plugin_manager.register("core", "core")
plugin_manager.register("docker", "fred.docker")
plugin_manager.register("homeassistant", "fred.homeassistant")
plugin_manager.register("network", "fred.network")

print(plugin_manager.list())
print()

print(plugin_loader.load())
print()

plugin_manager.disable("docker")
print(plugin_loader.load())
print()

plugin_manager.enable("docker")
print(plugin_loader.load())
print()

plugin_manager.reload()
print(plugin_loader.load())
