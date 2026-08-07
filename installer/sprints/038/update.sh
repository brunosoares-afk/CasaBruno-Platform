#!/usr/bin/env bash

ROOT="/opt/CasaBruno-Platform"

echo
echo "========================================"
echo "         SPRINT 038"
echo "========================================"
echo

echo "Integrando Orchestrator + Dispatcher..."

cat > "$ROOT/backend/app/fred/orchestrator/orchestrator.py" << 'PY'
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from intent.engine import engine as intent
from router.router import router
from pipeline.pipeline import pipeline
from dispatcher.dispatcher import dispatcher

pipeline.steps=[]

pipeline.add("intent")
pipeline.add("router")
pipeline.add("skills")
pipeline.add("actions")

class Orchestrator:

    def execute(self,text):

        detected=intent.detect(text)

        service=router.route(detected)

        result=dispatcher.dispatch(service)

        return {
            "text":text,
            "intent":detected,
            "service":service,
            "result":result,
            "pipeline":pipeline.execute()
        }

orchestrator=Orchestrator()
PY

cat > "$ROOT/backend/app/fred/orchestrator/test.py" << 'PY'
from orchestrator import orchestrator

print(orchestrator.execute("ligar luz"))
print(orchestrator.execute("temperatura"))
print(orchestrator.execute("docker"))
print(orchestrator.execute("rede"))
PY

echo
echo "[OK] Orchestrator integrado."
echo
