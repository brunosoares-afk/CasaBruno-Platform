#!/usr/bin/env bash

ROOT="/opt/CasaBruno-Platform"

echo
echo "========================================"
echo "         SPRINT 027"
echo "========================================"
echo

echo "Instalando Event Bus..."

mkdir -p "$ROOT/backend/app/fred/events"

touch "$ROOT/backend/app/fred/events/__init__.py"

cat > "$ROOT/backend/app/fred/events/bus.py" << 'PY'
class EventBus:

    def __init__(self):
        self.events=[]

    def emit(self,name,payload=None):
        self.events.append({
            "event":name,
            "payload":payload
        })

    def history(self):
        return self.events

bus=EventBus()
PY

cat > "$ROOT/backend/app/fred/events/test.py" << 'PY'
from bus import bus

bus.emit("system.boot")
bus.emit("docker.started",{"container":"homeassistant"})
bus.emit("ha.connected")

print(bus.history())
PY

echo
echo "[OK] Event Bus instalado."
echo
