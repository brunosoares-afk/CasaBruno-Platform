from tuya_connector import TuyaOpenAPI

API_ENDPOINT="https://openapi.tuyaus.com"

ACCESS_ID="k7qaqr9mxkdp89g4dhf9"
ACCESS_KEY="b69b8717f9a241148540d2ef76f4d2ac"

api=TuyaOpenAPI(
    API_ENDPOINT,
    ACCESS_ID,
    ACCESS_KEY
)

api.connect()

def status(device):
    return api.get(f"/v1.0/devices/{device}")

def functions(device):
    return api.get(f"/v1.0/devices/{device}/functions")

def specifications(device):
    return api.get(f"/v1.0/devices/{device}/specifications")

def commands(device):
    return api.get(f"/v1.0/devices/{device}/commands")

def get_device_info(device_id):
    r = api.get(f"/v1.0/devices/{device_id}")

    if isinstance(r, dict):
        return r

    return r.json()
