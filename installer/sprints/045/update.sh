#!/usr/bin/env bash

ROOT="/opt/CasaBruno-Platform"

echo
echo "========================================"
echo "         SPRINT 045"
echo "========================================"
echo

echo "Integrando Dashboard com API..."

cat > "$ROOT/backend/app/api/main.py" << 'PY'
from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from fred.orchestrator.orchestrator import Orchestrator

app = FastAPI(title="CBOS API")

fred = Orchestrator()

FRONTEND = Path("/opt/CasaBruno-Platform/frontend")

class Request(BaseModel):
    text:str

@app.get("/")
def dashboard():
    return FileResponse(FRONTEND / "index.html")

@app.get("/api/status")
def status():
    return {
        "platform":"CasaBruno Operating System",
        "ai":"FRED",
        "status":"online",
        "version":"1.0.0"
    }

@app.post("/api/fred")
def ask(req:Request):
    return fred.execute(req.text)
PY

cat > "$ROOT/frontend/js/app.js" << 'JS'
fetch("/api/status")
.then(r=>r.json())
.then(data=>{

document.getElementById("status").innerHTML=`
<h2>${data.platform}</h2>

<p><b>AI:</b> ${data.ai}</p>

<p><b>Status:</b>
<span style="color:lime">${data.status}</span></p>

<p><b>Version:</b> ${data.version}</p>
`;

})
.catch(()=>{

document.getElementById("status").innerHTML="API Offline";

});
JS

systemctl restart cbos-api

echo
echo "[OK] Dashboard integrado."
echo
