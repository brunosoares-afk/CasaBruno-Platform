#!/usr/bin/env bash

ROOT="/opt/CasaBruno-Platform"

echo
echo "========================================"
echo "         SPRINT 039"
echo "========================================"
echo

echo "Instalando Executor Engine..."

mkdir -p "$ROOT/backend/app/fred/executor"

touch "$ROOT/backend/app/fred/executor/__init__.py"

cat > "$ROOT/backend/app/fred/executor/executor.py" << 'PY'
from dispatcher.dispatcher import dispatcher

class Executor:

    def execute(self,service):

        return {
            "status":"success",
            "service":service,
            "response":dispatcher.dispatch(service)
        }

executor=Executor()
PY

cat > "$ROOT/backend/app/fred/executor/test.py" << 'PY'
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))

from executor import executor

print(executor.execute("LightService"))
print(executor.execute("WeatherService"))
print(executor.execute("DockerService"))
print(executor.execute("NetworkService"))
print(executor.execute("HomeAssistantService"))
print(executor.execute("FallbackService"))
PY

echo
echo "[OK] Executor Engine instalado."
echo
