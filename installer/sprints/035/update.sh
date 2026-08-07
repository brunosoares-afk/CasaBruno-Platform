#!/usr/bin/env bash

ROOT="/opt/CasaBruno-Platform"

echo
echo "========================================"
echo "         SPRINT 035"
echo "========================================"
echo

echo "Instalando AI Runtime..."

mkdir -p "$ROOT/backend/app/fred/runtime"

touch "$ROOT/backend/app/fred/runtime/__init__.py"

cat > "$ROOT/backend/app/fred/runtime/runtime.py" << 'PY'
from datetime import datetime

class Runtime:

    def __init__(self):
        self.started=datetime.now()
        self.state="online"

    def uptime(self):
        return str(datetime.now()-self.started)

    def status(self):
        return {
            "state":self.state,
            "uptime":self.uptime()
        }

runtime=Runtime()
PY

cat > "$ROOT/backend/app/fred/runtime/test.py" << 'PY'
from runtime import runtime
import time

print(runtime.status())

time.sleep(2)

print(runtime.status())
PY

echo
echo "[OK] AI Runtime instalado."
echo
