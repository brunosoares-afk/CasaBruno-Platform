from app.integrations.tuya.client import api
import json

uid = "az1773074245562AmZTG"

r = api.get(f"/v1.0/users/{uid}/devices")

if isinstance(r, dict):
    print(json.dumps(r, indent=4, ensure_ascii=False))
else:
    try:
        print(json.dumps(r.json(), indent=4, ensure_ascii=False))
    except Exception:
        print(r.text)
