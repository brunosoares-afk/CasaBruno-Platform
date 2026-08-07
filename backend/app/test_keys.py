from app.integrations.tuya.client import api
import json

hub = "ebd5e5ed961cfe1111txzq"
remote = "eba153d0e197b62eeap9ia"

urls = [
    f"/v2.0/infrareds/{hub}/remotes/{remote}/keys",
    f"/v1.0/infrareds/{hub}/remotes/{remote}/keys",
    f"/v2.0/infrareds/{hub}/remotes/{remote}",
    f"/v1.0/infrareds/{hub}/remotes/{remote}",
    f"/v2.0/infrareds/{hub}/remotes/{remote}/commands",
    f"/v1.0/infrareds/{hub}/remotes/{remote}/commands",
]

for url in urls:
    print("=" * 80)
    print(url)

    r = api.get(url)

    if isinstance(r, dict):
        print(json.dumps(r, indent=4, ensure_ascii=False))
    else:
        try:
            print(json.dumps(r.json(), indent=4, ensure_ascii=False))
        except:
            print(r.text)
