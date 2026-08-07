from app.core.plugins.plugin import Plugin


class PluginsAPI:

    VERSION = "2.0.0"

    def __init__(self):
        self.plugins = {}

    def register(self, name, description=""):

        if name not in self.plugins:
            self.plugins[name] = Plugin(
                name,
                description
            )

        return self.plugins[name].status()

    def list(self):
        return list(self.plugins.keys())

    def all(self):
        return [
            plugin.status()
            for plugin in self.plugins.values()
        ]

    def get(self, name):
        plugin = self.plugins.get(name)

        if plugin is None:
            return None

        return plugin.status()

    def load(self, name):

        plugin = self.plugins.get(name)

        if plugin is None:
            return None

        return plugin.load()

    def unload(self, name):

        plugin = self.plugins.get(name)

        if plugin is None:
            return None

        return plugin.unload()

    def enable(self, name):

        plugin = self.plugins.get(name)

        if plugin is None:
            return None

        return plugin.enable()

    def disable(self, name):

        plugin = self.plugins.get(name)

        if plugin is None:
            return None

        return plugin.disable()

    def count(self):
        return len(self.plugins)

    def summary(self):
        return {
            "version": self.VERSION,
            "plugins": self.count()
        }


api = PluginsAPI()
