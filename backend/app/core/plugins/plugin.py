from datetime import datetime


class Plugin:

    VERSION = "2.0.0"

    def __init__(self, name, description=""):
        self.name = name
        self.description = description

        self.enabled = False
        self.loaded = False

        self.created = datetime.now().isoformat(timespec="seconds")
        self.loaded_at = None

    def load(self):
        self.loaded = True
        self.loaded_at = datetime.now().isoformat(timespec="seconds")
        return self.status()

    def unload(self):
        self.loaded = False
        return self.status()

    def enable(self):
        self.enabled = True
        return self.status()

    def disable(self):
        self.enabled = False
        return self.status()

    def status(self):
        return {
            "name": self.name,
            "description": self.description,
            "enabled": self.enabled,
            "loaded": self.loaded,
            "created": self.created,
            "loaded_at": self.loaded_at
        }


plugin = Plugin
