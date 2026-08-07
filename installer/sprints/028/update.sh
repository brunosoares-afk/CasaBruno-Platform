#!/usr/bin/env bash

ROOT="/opt/CasaBruno-Platform"

echo
echo "========================================"
echo "         SPRINT 028"
echo "========================================"
echo

echo "Instalando Scheduler..."

mkdir -p "$ROOT/backend/app/fred/scheduler"

touch "$ROOT/backend/app/fred/scheduler/__init__.py"

cat > "$ROOT/backend/app/fred/scheduler/scheduler.py" << 'PY'
import time

class Scheduler:

    def __init__(self):
        self.jobs=[]

    def add(self,name,interval):
        self.jobs.append({
            "name":name,
            "interval":interval
        })

    def list(self):
        return self.jobs

scheduler=Scheduler()
PY

cat > "$ROOT/backend/app/fred/scheduler/test.py" << 'PY'
from scheduler import scheduler

scheduler.add("health-check",30)
scheduler.add("docker-scan",60)
scheduler.add("ha-sync",120)

print(scheduler.list())
PY

echo
echo "[OK] Scheduler instalado."
echo
