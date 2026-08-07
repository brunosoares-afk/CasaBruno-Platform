from datetime import datetime


class PluginManager:

    def __init__(self):

        self.plugins = {}

    def register(self, name, version="1.0.0"):

        self.plugins[name] = {

            "version": version,

            "enabled": True,

            "loaded": datetime.now().isoformat()

        }

    def enable(self, name):

        if name in self.plugins:

            self.plugins[name]["enabled"] = True

    def disable(self, name):

        if name in self.plugins:

            self.plugins[name]["enabled"] = False

    def list(self):

        return self.plugins


plugin_manager = PluginManager()


plugin_manager.register("core")
plugin_manager.register("fred")
plugin_manager.register("homeassistant")
plugin_manager.register("docker")
plugin_manager.register("registry")
plugin_manager.register("scheduler")
plugin_manager.register("events")
plugin_manager.register("ollama")
