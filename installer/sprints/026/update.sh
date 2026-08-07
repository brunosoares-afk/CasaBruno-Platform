#!/usr/bin/env bash

ROOT="/opt/CasaBruno-Platform"

echo
echo "========================================"
echo "         SPRINT 026"
echo "========================================"
echo

echo "Instalando Network Connector..."

mkdir -p "$ROOT/backend/app/fred/network"

touch "$ROOT/backend/app/fred/network/__init__.py"

cat > "$ROOT/backend/app/fred/network/client.py" << 'PY'
import subprocess

class NetworkClient:

    def ping(self,host):

        try:
            subprocess.check_output(
                ["ping","-c","1","-W","1",host],
                stderr=subprocess.DEVNULL
            )
            return True

        except Exception:
            return False

network=NetworkClient()
PY

cat > "$ROOT/backend/app/fred/network/test.py" << 'PY'
from client import network

print("Gateway :",network.ping("192.168.15.1"))
print("HA      :",network.ping("192.168.15.10"))
print("Google  :",network.ping("8.8.8.8"))
PY

echo
echo "[OK] Network Connector instalado."
echo
