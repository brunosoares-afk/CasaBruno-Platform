from app.integrations.tuya.client import api
from app.integrations.tuya.devices import SMART_IR

TV = "eba153d0e197b62eeap9ia"
AIR = "ebfd426b126b4752151ox3"
PROJECTOR = "ebad5da8824a00c518kage"


def send(remote, category, key):
    return api.post(
        f"/v2.0/infrareds/{SMART_IR}/remotes/{remote}/command",
        {
            "categoryId": category,
            "key": key
        }
    )


def tv(key):
    return send(TV, 2, key)


def projector(key):
    return send(PROJECTOR, 6, key)


def air(key):
    return send(AIR, 5, key)
