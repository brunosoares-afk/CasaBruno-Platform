from app.integrations.tuya.client import api
import json
import time

HUB = "ebd5e5ed961cfe1111txzq"
REMOTE = "ebfd426b126b4752151ox3"

commands = [
    "PowerOn",
    "PowerOff",
    "M",
    "F",
    "T",
]

for cmd in commands:
    print("=" * 60)
    print(cmd)

    r = api.post(
        f"/v1.0/infrareds/{HUB}/remotes/{REMOTE}/command",
        {
            "key": cmd
        }
    )

    print(json.dumps(r, indent=4))
    time.sleep(2)
