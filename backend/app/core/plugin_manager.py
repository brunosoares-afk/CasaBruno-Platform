from datetime import datetime


class PluginManager:

    def __init__(self):
        self.plugins = {}

    def register(self, name, module=None, version="1.0.0"):

        if module is None:
            module = name

        self.plugins[name] = {
            "name": name,
            "module": module,
            "version": version,
            "enabled": True,
            "loaded": datetime.now().isoformat()
        }

    def unregister(self, name):
        self.plugins.pop(name, None)

    def enable(self, name):
        if name in self.plugins:
            self.plugins[name]["enabled"] = True

    def disable(self, name):
        if name in self.plugins:
            self.plugins[name]["enabled"] = False

    def get(self, name):
        return self.plugins.get(name)

    def list(self):
        return self.plugins

    def reload(self):

        plugins = list(self.plugins.values())

        self.plugins.clear()

        for plugin in plugins:
            self.register(
                plugin["name"],
                plugin["module"],
                plugin["version"]
            )

        return self.plugins


plugin_manager = PluginManager()
