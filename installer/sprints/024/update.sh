#!/usr/bin/env bash

ROOT="/opt/CasaBruno-Platform"

echo
echo "========================================"
echo "         SPRINT 024"
echo "========================================"
echo

echo "Instalando Home Assistant Connector..."

mkdir -p "$ROOT/backend/app/fred/homeassistant"

touch "$ROOT/backend/app/fred/homeassistant/__init__.py"

cat > "$ROOT/backend/app/fred/homeassistant/client.py" << 'PY'
class HomeAssistantClient:

    def __init__(self):
        self.host="192.168.15.10"
        self.port=8123

    def status(self):
        return {
            "service":"homeassistant",
            "host":self.host,
            "port":self.port,
            "status":"online"
        }

ha=HomeAssistantClient()
PY

cat > "$ROOT/backend/app/fred/homeassistant/test.py" << 'PY'
from client import ha

print(ha.status())
PY

echo
echo "[OK] Home Assistant Connector instalado."
echo
