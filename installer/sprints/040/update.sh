#!/usr/bin/env bash

ROOT="/opt/CasaBruno-Platform"

echo
echo "========================================"
echo "         SPRINT 040"
echo "========================================"
echo

echo "Instalando API Gateway..."

mkdir -p "$ROOT/backend/app/api"

touch "$ROOT/backend/app/api/__init__.py"

cat > "$ROOT/backend/app/api/main.py" << 'PY'
from fastapi import FastAPI
from pydantic import BaseModel

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from fred.orchestrator.orchestrator import Orchestrator

app = FastAPI(title="CBOS API")

fred = Orchestrator()

class Request(BaseModel):
    text: str

@app.get("/")
def root():
    return {
        "platform":"CasaBruno Operating System",
        "ai":"FRED",
        "status":"online"
    }

@app.post("/fred")
def ask(req: Request):
    return fred.execute(req.text)
PY

cat > "$ROOT/backend/app/api/test.py" << 'PY'
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from api.main import app

print(app.title)

for r in app.routes:
    print(r.path)
PY

echo
echo "[OK] API Gateway instalado."
echo
