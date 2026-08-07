from datetime import datetime


class Event:

    VERSION = "2.0.0"

    def __init__(self, name, payload=None):
        self.name = name
        self.payload = payload or {}

        self.created = datetime.now().isoformat(timespec="seconds")
        self.processed = False
        self.processed_at = None

    def process(self):
        self.processed = True
        self.processed_at = datetime.now().isoformat(timespec="seconds")
        return self.status()

    def status(self):
        return {
            "name": self.name,
            "payload": self.payload,
            "created": self.created,
            "processed": self.processed,
            "processed_at": self.processed_at
        }


event = Event
