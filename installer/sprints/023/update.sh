#!/usr/bin/env bash

ROOT="/opt/CasaBruno-Platform"

echo
echo "========================================"
echo "         SPRINT 023"
echo "========================================"
echo

echo "Instalando Device Registry..."

mkdir -p "$ROOT/backend/app/fred/registry"

touch "$ROOT/backend/app/fred/registry/__init__.py"

cat > "$ROOT/backend/app/fred/registry/registry.py" << 'PY'
class DeviceRegistry:

    def __init__(self):
        self.devices={}

    def add(self,name,ip,kind):
        self.devices[name]={
            "ip":ip,
            "type":kind
        }

    def get(self,name):
        return self.devices.get(name)

    def all(self):
        return self.devices

registry=DeviceRegistry()
PY

cat > "$ROOT/backend/app/fred/registry/test.py" << 'PY'
from registry import registry

registry.add("HomeAssistant","192.168.15.10","ha")
registry.add("Mikrotik","192.168.15.1","router")
registry.add("NAS","192.168.15.20","storage")

print(registry.get("HomeAssistant"))
print(registry.get("Mikrotik"))
print(registry.all())
PY

echo
echo "[OK] Device Registry instalado."
echo
