from app.integrations.tuya.client import api
import json

HUB = "ebd5e5ed961cfe1111txzq"
REMOTE = "ebfd426b126b4752151ox3"

r = api.get(
    f"/v1.0/infrareds/{HUB}/remotes/{REMOTE}/keys"
)

print(json.dumps(r, indent=4))
