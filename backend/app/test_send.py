from app.integrations.tuya.client import api
import json

hub="ebd5e5ed961cfe1111txzq"
remote="eba153d0e197b62eeap9ia"

tests=[
("/v2.0/infrareds/{}/remotes/{}/command".format(hub,remote),{"key":"Power"}),
("/v2.0/infrareds/{}/remotes/{}/command".format(hub,remote),{"key_id":1}),
("/v2.0/infrareds/{}/remotes/{}/commands".format(hub,remote),{"key":"Power"}),
("/v2.0/infrareds/{}/remotes/{}/commands".format(hub,remote),{"key_id":1}),
("/v1.0/infrareds/{}/remotes/{}/command".format(hub,remote),{"key":"Power"}),
("/v1.0/infrareds/{}/remotes/{}/command".format(hub,remote),{"key_id":1}),
("/v1.0/infrareds/{}/remotes/{}/commands".format(hub,remote),{"key":"Power"}),
("/v1.0/infrareds/{}/remotes/{}/commands".format(hub,remote),{"key_id":1}),
]

for url,body in tests:
    print("="*80)
    print(url)
    print(body)

    r=api.post(url,body)

    if isinstance(r,dict):
        print(json.dumps(r,indent=4,ensure_ascii=False))
    else:
        try:
            print(json.dumps(r.json(),indent=4,ensure_ascii=False))
        except:
            print(r.text)
