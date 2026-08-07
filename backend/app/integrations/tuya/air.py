from .client import api
from .devices import AIR

def power(on):
    return api.post(
        f"/v1.0/devices/{AIR}/commands",
        {
            "commands": [
                {
                    "code": "switch",
                    "value": on
                }
            ]
        }
    )

def temperature(temp):
    return api.post(
        f"/v1.0/devices/{AIR}/commands",
        {
            "commands": [
                {
                    "code": "temp",
                    "value": temp
                }
            ]
        }
    )

def mode(mode):
    return api.post(
        f"/v1.0/devices/{AIR}/commands",
        {
            "commands": [
                {
                    "code": "mode",
                    "value": mode
                }
            ]
        }
    )

def fan(speed):
    return api.post(
        f"/v1.0/devices/{AIR}/commands",
        {
            "commands": [
                {
                    "code": "fan",
                    "value": speed
                }
            ]
        }
    )
