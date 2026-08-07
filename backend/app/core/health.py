from datetime import datetime
import socket

from config.settings import settings


class HealthCheck:

    def status(self):

        return {

            "online": True,

            "project": settings.PROJECT_NAME,

            "version": settings.VERSION,

            "hostname": socket.gethostname(),

            "timestamp": datetime.now().isoformat(),

            "services": {

                "core": "online",

                "fred": "online",

                "homeassistant": "pending",

                "ollama": "pending"

            }

        }


health = HealthCheck()
