from app.integrations.tuya.client import api
import json

hub = "ebd5e5ed961cfe1111txzq"

urls = [
    f"/v2.0/infrareds/{hub}/remotes",
    f"/v2.0/infrareds/{hub}/categories",
    f"/v2.0/infrareds/{hub}",
    f"/v1.0/infrareds/{hub}/remotes",
    f"/v1.0/infrareds/{hub}",
]

for u in urls:
    print("="*80)
    print(u)

    r = api.get(u)

    if isinstance(r, dict):
        print(json.dumps(r, indent=4, ensure_ascii=False))
    else:
        try:
            print(json.dumps(r.json(), indent=4, ensure_ascii=False))
        except Exception:
            print(r.text)
