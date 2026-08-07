import routeros_api

from app.core.config.config import config


class MikrotikClient:

    def __init__(self):
        self.reload()

    def reload(self):
        cfg = config.get("mikrotik", {}) or {}
        self.host = cfg.get("host", "192.168.2.1")
        self.port = cfg.get("port", 8728)
        self.user = cfg.get("user", "")
        self.password = cfg.get("password", "")

    def connect(self):
        self.reload()
        pool = routeros_api.RouterOsApiPool(
            self.host,
            username=self.user,
            password=self.password,
            port=self.port,
            plaintext_login=True
        )
        return pool.get_api(), pool

    def identity(self):
        api, pool = self.connect()
        try:
            data = api.get_resource("/system/identity").get()
            return data[0] if data else {}
        finally:
            pool.disconnect()

    def resource(self):
        api, pool = self.connect()
        try:
            data = api.get_resource("/system/resource").get()
            return data[0] if data else {}
        finally:
            pool.disconnect()

    def interfaces(self):
        api, pool = self.connect()
        try:
            return api.get_resource("/interface").get()
        finally:
            pool.disconnect()


mikrotik_client = MikrotikClient()
