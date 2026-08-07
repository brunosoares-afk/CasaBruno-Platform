from app.integrations.tuya.client import api
import json

HUB = "ebd5e5ed961cfe1111txzq"
REMOTE = "eba153d0e197b62eeap9ia"

keys = [
    "Power",
    "Volume+",
    "Volume-",
    "Channel+",
    "Channel-",
    "Menu",
    "Up",
    "Down",
    "Left",
    "Right"
]

for k in keys:
    print("=" * 60)
    print("Enviando:", k)

    r = api.post(
        f"/v1.0/infrareds/{HUB}/remotes/{REMOTE}/command",
        {"key": k}
    )

    print(json.dumps(r, indent=4, ensure_ascii=False))
