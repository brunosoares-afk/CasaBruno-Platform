from .client import api
from .devices import TV

def power(on):
    return api.post(
        f"/v1.0/devices/{TV}/commands",
        {
            "commands": [
                {
                    "code": "switch",
                    "value": on
                }
            ]
        }
    )

def volume(step):
    return api.post(
        f"/v1.0/devices/{TV}/commands",
        {
            "commands": [
                {
                    "code": "volume_control",
                    "value": step
                }
            ]
        }
    )

def channel(step):
    return api.post(
        f"/v1.0/devices/{TV}/commands",
        {
            "commands": [
                {
                    "code": "channel_control",
                    "value": step
                }
            ]
        }
    )
