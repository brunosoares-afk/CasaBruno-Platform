from datetime import datetime


class Service:

    VERSION = "2.0.0"

    def __init__(self, name, description=""):
        self.name = name
        self.description = description

        self.running = False
        self.started = None
        self.stopped = None

    def start(self):
        self.running = True
        self.started = datetime.now().isoformat(timespec="seconds")

        return self.status()

    def stop(self):
        self.running = False
        self.stopped = datetime.now().isoformat(timespec="seconds")

        return self.status()

    def restart(self):
        self.stop()
        return self.start()

    def status(self):
        return {
            "name": self.name,
            "description": self.description,
            "running": self.running,
            "started": self.started,
            "stopped": self.stopped
        }


service = Service(
    "generic",
    "Generic Service"
)
