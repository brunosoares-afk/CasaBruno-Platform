from app.integrations.tuya.client import api
import json
import time

HUB = "ebd5e5ed961cfe1111txzq"
REMOTE = "ebfd426b126b4752151ox3"

comandos = [
    "Power",
    "Mode",
    "Temp+",
    "Temp-",
    "Wind",
    "Swing",
    "Auto",
    "Cool",
    "Heat",
    "Dry",
]

for cmd in comandos:
    print("=" * 60)
    print("Enviando:", cmd)

    r = api.post(
        f"/v1.0/infrareds/{HUB}/remotes/{REMOTE}/command",
        {"key": cmd}
    )

    print(json.dumps(r, indent=4))
    time.sleep(2)
