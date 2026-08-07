#!/usr/bin/env bash

ROOT="/opt/CasaBruno-Platform"

echo
echo "========================================"
echo "         SPRINT 021"
echo "========================================"
echo

echo "Instalando Intent Router..."

mkdir -p "$ROOT/backend/app/fred/router"

touch "$ROOT/backend/app/fred/router/__init__.py"

cat > "$ROOT/backend/app/fred/router/router.py" << 'PY'
from intent.engine import engine

class IntentRouter:

    def route(self,text):

        intent=engine.detect(text)

        routes={
            "light":"LightService",
            "weather":"WeatherService",
            "docker":"DockerService",
            "unknown":"FallbackService"
        }

        return routes.get(intent,"FallbackService")

router=IntentRouter()
PY

cat > "$ROOT/backend/app/fred/router/test.py" << 'PY'
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))

from router.router import router

print(router.route("acender luz"))
print(router.route("temperatura"))
print(router.route("docker"))
print(router.route("teste"))
PY

echo
echo "[OK] Intent Router instalado."
echo
