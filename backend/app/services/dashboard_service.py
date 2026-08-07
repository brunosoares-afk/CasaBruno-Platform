from app.services.system import get_system_status
from app.services.docker_service import get_containers
from app.services.homeassistant_service import get_homeassistant_status


def get_dashboard():

    system = get_system_status()

    containers = get_containers()

    ha = get_homeassistant_status()

    return {

        "system": system,

        "docker": {

            "online": True,

            "containers": len(containers),

            "running": len(
                [c for c in containers if c["status"] == "running"]
            ),

            "list": containers

        },

        "homeassistant": ha

    }
