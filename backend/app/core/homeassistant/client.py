import requests

from app.core.config.config import config


class HomeAssistantClient:

    def __init__(self):
        self.reload()

    def reload(self):
        cfg = config.get("homeassistant")

        self.host = cfg.get("host", "127.0.0.1")
        self.port = cfg.get("port", 8123)
        self.ssl = cfg.get("ssl", False)
        self.token = cfg.get("token", "")

        protocol = "https" if self.ssl else "http"
        self.base = f"{protocol}://{self.host}:{self.port}/api"

    def headers(self):
        headers = {
            "Content-Type": "application/json"
        }

        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        return headers

    def get(self, endpoint):
        self.reload()
        r = requests.get(
            self.base + endpoint,
            headers=self.headers(),
            timeout=10
        )
        return r.json()

    def post(self, endpoint, data=None):
        self.reload()

        if data is None:
            data = {}

        r = requests.post(
            self.base + endpoint,
            json=data,
            headers=self.headers(),
            timeout=10
        )
        return r.json()

    def get_raw(self, endpoint):
        self.reload()
        return requests.get(
            self.base + endpoint,
            headers=self.headers(),
            timeout=10
        )

    def states(self):
        return self.get("/states")

    def services(self):
        return self.get("/services")

    def call_service(self, domain, service, data=None):
        return self.post(
            f"/services/{domain}/{service}",
            data
        )


ha_client = HomeAssistantClient()
