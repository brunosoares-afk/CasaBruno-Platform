#!/usr/bin/env bash

ROOT="/opt/CasaBruno-Platform"

echo
echo "========================================"
echo "         SPRINT 047"
echo "========================================"
echo

echo "Instalando System Monitor..."

mkdir -p "$ROOT/backend/app/system"

touch "$ROOT/backend/app/system/__init__.py"

cat > "$ROOT/backend/app/system/system.py" << 'PY'
import shutil
import platform
import socket
import os

try:
    import psutil
except:
    psutil = None


class System:

    def info(self):

        total, used, free = shutil.disk_usage("/")

        return {
            "hostname": socket.gethostname(),
            "os": platform.system(),
            "release": platform.release(),
            "cpu": psutil.cpu_percent() if psutil else 0,
            "memory": psutil.virtual_memory().percent if psutil else 0,
            "disk": round((used / total) * 100, 2)
        }


system = System()
PY

cat > "$ROOT/backend/app/system/test.py" << 'PY'
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from system.system import system

print(system.info())
PY

python3 "$ROOT/backend/app/system/test.py"

echo
echo "[OK] System Monitor instalado."

