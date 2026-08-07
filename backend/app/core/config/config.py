import json
from pathlib import Path


class Config:

    VERSION = "2.0.0"

    def __init__(self):
        self.base = Path(__file__).resolve().parents[2]
        self.file = self.base / "config.json"
        self.data = {}
        self.load()

    def load(self):

        if self.file.exists():
            with open(self.file, "r", encoding="utf-8") as f:
                self.data = json.load(f)
        else:
            self.data = {
                "application": {
                    "name": "CasaBruno Platform",
                    "version": self.VERSION
                },
                "homeassistant": {
                    "host": "192.168.15.10",
                    "port": 8123,
                    "ssl": False,
                    "token": ""
                },
                "docker": {
                    "enabled": True
                },
                "network": {
                    "gateway": "192.168.2.1",
                    "dns": "8.8.8.8"
                }
            }
            self.save()

        return self.data

    def save(self):
        with open(self.file, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=4)
        return True

    def all(self):
        return self.data

    def get(self, section, default=None):
        return self.data.get(section, default)

    def set(self, section, value):
        self.data[section] = value
        self.save()
        return True

    def delete(self, section):
        if section in self.data:
            del self.data[section]
            self.save()
            return True
        return False

    def exists(self, section):
        return section in self.data

    def sections(self):
        return list(self.data.keys())

    def summary(self):
        return {
            "version": self.VERSION,
            "file": str(self.file),
            "loaded": True,
            "sections": self.sections()
        }


config = Config()
