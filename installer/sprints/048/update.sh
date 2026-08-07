#!/usr/bin/env bash

ROOT="/opt/CasaBruno-Platform"

echo
echo "========================================"
echo "         SPRINT 048"
echo "========================================"
echo

echo "Integrando Monitor do Sistema..."

cat > "$ROOT/backend/app/api/main.py" << 'PY'
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
import sys

APP = Path("/opt/CasaBruno-Platform/backend/app")
FRONT = Path("/opt/CasaBruno-Platform/frontend")

sys.path.insert(0, str(APP))

from system.system import system

app = FastAPI(title="CasaBruno Platform")

app.mount("/css", StaticFiles(directory=FRONT/"css"), name="css")
app.mount("/js", StaticFiles(directory=FRONT/"js"), name="js")
app.mount("/assets", StaticFiles(directory=FRONT/"assets"), name="assets")

@app.get("/")
def home():
    return FileResponse(FRONT/"index.html")

@app.get("/api/status")
def status():
    return {
        "platform":"CasaBruno Operating System",
        "ai":"FRED",
        "status":"online",
        "version":"1.0.0"
    }

@app.get("/api/system")
def system_info():
    return system.info()

@app.get("/health")
def health():
    return {"status":"ok"}
PY

cat > "$ROOT/frontend/js/app.js" << 'JS'
async function updateDashboard(){

    try{

        const status=await fetch("/api/status");
        const info=await fetch("/api/system");

        const s=await status.json();
        const i=await info.json();

        document.getElementById("status").innerHTML=`
<div class="card">
<h2>${s.platform}</h2>

<p><b>AI:</b> ${s.ai}</p>
<p><b>Status:</b> ${s.status}</p>
<p><b>Versão:</b> ${s.version}</p>

<hr>

<p><b>Hostname:</b> ${i.hostname}</p>
<p><b>Sistema:</b> ${i.os} ${i.release}</p>
<p><b>CPU:</b> ${i.cpu}%</p>
<p><b>Memória:</b> ${i.memory}%</p>
<p><b>Disco:</b> ${i.disk}%</p>

<hr>

<p><b>Atualizado:</b> ${new Date().toLocaleTimeString()}</p>

</div>
`;

    }catch(e){

        document.getElementById("status").innerHTML="<h2>API OFFLINE</h2>";

    }

}

updateDashboard();

setInterval(updateDashboard,3000);
JS

systemctl restart cbos-api

sleep 2

echo
echo "[OK] Dashboard integrado ao Monitor do Sistema."

curl -s http://127.0.0.1:8080/api/system

echo

