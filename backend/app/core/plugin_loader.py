import importlib

from app.core.plugin_manager import plugin_manager


class PluginLoader:

    def load(self):

        loaded = []

        for plugin in plugin_manager.list().values():

            if not plugin["enabled"]:
                continue

            try:
                importlib.import_module(plugin["module"])
                loaded.append(plugin["name"])

            except Exception:
                pass

        return loaded

    def reload(self):
        return self.load()


plugin_loader = PluginLoader()
