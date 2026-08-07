from app.integrations.tuya.client import api
import json

HUB = "ebd5e5ed961cfe1111txzq"
REMOTE = "ebfd426b126b4752151ox3"

for url in [
    f"/v2.0/infrareds/{HUB}/remotes/{REMOTE}/ac/status",
    f"/v1.0/infrareds/{HUB}/remotes/{REMOTE}/ac/status",
    f"/v2.0/infrareds/{HUB}/remotes/{REMOTE}/status",
    f"/v1.0/infrareds/{HUB}/remotes/{REMOTE}/status",
]:
    print("=" * 80)
    print(url)

    try:
        r = api.get(url)
        print(json.dumps(r, indent=4))
    except Exception as e:
        print(e)
