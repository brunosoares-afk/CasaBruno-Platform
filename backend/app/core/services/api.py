from app.core.services.service import Service


class ServicesAPI:

    VERSION = "2.0.0"

    def __init__(self):
        self.services = {}

    def register(self, name, description=""):

        if name not in self.services:
            self.services[name] = Service(
                name,
                description
            )

        return self.services[name].status()

    def list(self):
        return list(self.services.keys())

    def all(self):
        return [
            service.status()
            for service in self.services.values()
        ]

    def get(self, name):
        service = self.services.get(name)

        if service is None:
            return None

        return service.status()

    def start(self, name):

        if name not in self.services:
            return None

        return self.services[name].start()

    def stop(self, name):

        if name not in self.services:
            return None

        return self.services[name].stop()

    def restart(self, name):

        if name not in self.services:
            return None

        return self.services[name].restart()

    def count(self):
        return len(self.services)

    def summary(self):
        return {
            "version": self.VERSION,
            "services": self.count()
        }


api = ServicesAPI()
