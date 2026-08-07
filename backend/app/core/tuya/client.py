from tuya_connector import TuyaOpenAPI

from .config import *

class TuyaClient:

    def __init__(self):
        self.api = TuyaOpenAPI(
            TUYA_BASE_URL,
            TUYA_CLIENT_ID,
            TUYA_CLIENT_SECRET
        )
        self.api.connect()

    def devices(self):
        return self.api.get("/v1.0/users/me/devices")

    def device(self, device_id):
        return self.api.get(f"/v1.0/devices/{device_id}")

    def commands(self, device_id, commands):
        return self.api.post(
            f"/v1.0/devices/{device_id}/commands",
            {"commands": commands},
        )

tuya = TuyaClient()
