#!/usr/bin/env bash

ROOT="/opt/CasaBruno-Platform"

echo
echo "========================================"
echo "         SPRINT 019"
echo "========================================"
echo

echo "Instalando FRED Core..."

mkdir -p "$ROOT/backend/app/fred"

touch "$ROOT/backend/app/fred/__init__.py"

cat > "$ROOT/backend/app/fred/core.py" << 'PY'
class FRED:

    VERSION="1.0.0"

    NAME="Friendly Responsive Executive Device"

    def start(self):
        return {
            "status":"online",
            "ai":"FRED",
            "version":self.VERSION
        }

fred=FRED()
PY

cat > "$ROOT/backend/app/fred/main.py" << 'PY'
from fred.core import fred

if __name__=="__main__":
    print(fred.start())
PY

echo
echo "[OK] FRED Core instalado."
echo
