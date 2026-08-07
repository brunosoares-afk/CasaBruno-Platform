#!/usr/bin/env bash

ROOT="/opt/CasaBruno-Platform"

echo
echo "========================================"
echo "         SPRINT 043"
echo "========================================"
echo

echo "Instalando Dashboard Backend..."

mkdir -p "$ROOT/backend/app/dashboard"

touch "$ROOT/backend/app/dashboard/__init__.py"

cat > "$ROOT/backend/app/dashboard/dashboard.py" << 'PY'
class Dashboard:

    def status(self):

        return {
            "platform":"CasaBruno Operating System",
            "ai":"FRED",
            "api":"online",
            "websocket":"online",
            "version":"1.0.0"
        }

dashboard=Dashboard()
PY

cat > "$ROOT/backend/app/dashboard/test.py" << 'PY'
from dashboard import dashboard

print(dashboard.status())
PY

echo
echo "[OK] Dashboard Backend instalado."
echo
