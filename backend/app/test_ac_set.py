from app.integrations.tuya.client import api
import json

HUB = "ebd5e5ed961cfe1111txzq"
REMOTE = "ebfd426b126b4752151ox3"

tests = [
    (
        "/v2.0/infrareds/{}/remotes/{}/ac/status".format(HUB, REMOTE),
        {
            "power":"1",
            "mode":"0",
            "temp":"24",
            "wind":"0"
        }
    ),
    (
        "/v1.0/infrareds/{}/remotes/{}/ac/status".format(HUB, REMOTE),
        {
            "power":"1",
            "mode":"0",
            "temp":"24",
            "wind":"0"
        }
    ),
]

for url,payload in tests:

    print("="*80)
    print(url)
    print(payload)

    r=api.post(url,payload)

    print(json.dumps(r,indent=4))
