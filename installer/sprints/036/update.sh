#!/usr/bin/env bash

ROOT="/opt/CasaBruno-Platform"

echo
echo "========================================"
echo "         SPRINT 036"
echo "========================================"
echo

echo "Instalando AI Orchestrator..."

mkdir -p "$ROOT/backend/app/fred/orchestrator"

touch "$ROOT/backend/app/fred/orchestrator/__init__.py"

cat > "$ROOT/backend/app/fred/orchestrator/orchestrator.py" << 'PY'
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from intent.engine import engine as intent
from router.router import router
from pipeline.pipeline import pipeline

class Orchestrator:

    def execute(self,text):

        i=intent.detect(text)
        s=router.route(i)

        return {
            "text":text,
            "intent":i,
            "service":s,
            "pipeline":pipeline.execute()
        }

orchestrator=Orchestrator()
PY

cat > "$ROOT/backend/app/fred/orchestrator/test.py" << 'PY'
from orchestrator import orchestrator

print(orchestrator.execute("ligar luz"))
print(orchestrator.execute("temperatura"))
print(orchestrator.execute("docker"))
PY

echo
echo "[OK] AI Orchestrator instalado."
echo
