from app.integrations.tuya.client import api
import json

HUB="ebd5e5ed961cfe1111txzq"
REMOTE="ebfd426b126b4752151ox3"

urls = [
    f"/v1.0/infrareds/{HUB}/remotes/{REMOTE}/ac",
    f"/v2.0/infrareds/{HUB}/remotes/{REMOTE}/ac",
    f"/v1.0/infrareds/{HUB}/remotes/{REMOTE}/air",
    f"/v2.0/infrareds/{HUB}/remotes/{REMOTE}/air",
    f"/v1.0/infrareds/{HUB}/remotes/{REMOTE}/aircondition",
    f"/v2.0/infrareds/{HUB}/remotes/{REMOTE}/aircondition",
    f"/v1.0/infrareds/{HUB}/remotes/{REMOTE}/control",
    f"/v2.0/infrareds/{HUB}/remotes/{REMOTE}/control",
]

for url in urls:
    print("="*80)
    print(url)
    r = api.get(url)
    print(json.dumps(r, indent=4))
