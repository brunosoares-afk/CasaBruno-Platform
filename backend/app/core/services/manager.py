from datetime import datetime


class ServiceManager:

    def __init__(self):

        self.started = datetime.now()

        self.services = {}

    def register(self, name, status="online"):

        self.services[name] = {

            "status": status,

            "registered": datetime.now().isoformat()

        }

    def update(self, name, status):

        if name in self.services:

            self.services[name]["status"] = status

    def list(self):

        return self.services

    def health(self):

        return {

            "total": len(self.services),

            "online": len(

                [

                    s

                    for s in self.services.values()

                    if s["status"] == "online"

                ]

            ),

            "services": self.services

        }


service_manager = ServiceManager()

service_manager.register("core")

service_manager.register("fred")

service_manager.register("homeassistant")

service_manager.register("docker")

service_manager.register("registry")

service_manager.register("ollama")
