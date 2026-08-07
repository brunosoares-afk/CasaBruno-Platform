#!/usr/bin/env bash

ROOT="/opt/CasaBruno-Platform"

echo
echo "========================================"
echo "         SPRINT 020"
echo "========================================"
echo

echo "Instalando Intent Engine..."

mkdir -p "$ROOT/backend/app/fred/intent"

touch "$ROOT/backend/app/fred/intent/__init__.py"

cat > "$ROOT/backend/app/fred/intent/engine.py" << 'PY'
class IntentEngine:

    def detect(self,text):

        text=text.lower()

        if "luz" in text:
            return "light"

        if "clima" in text:
            return "weather"

        if "temperatura" in text:
            return "weather"

        if "docker" in text:
            return "docker"

        return "unknown"

engine=IntentEngine()
PY

cat > "$ROOT/backend/app/fred/intent/test.py" << 'PY'
from engine import engine

print(engine.detect("acender luz"))
print(engine.detect("temperatura"))
print(engine.detect("docker"))
print(engine.detect("qualquer coisa"))
PY

echo
echo "[OK] Intent Engine instalado."
echo
