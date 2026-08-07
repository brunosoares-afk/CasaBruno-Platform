#!/usr/bin/env bash

ROOT="/opt/CasaBruno-Platform"

echo
echo "========================================"
echo "         SPRINT 030"
echo "========================================"
echo

echo "Instalando Action Engine..."

mkdir -p "$ROOT/backend/app/fred/actions"

touch "$ROOT/backend/app/fred/actions/__init__.py"

cat > "$ROOT/backend/app/fred/actions/engine.py" << 'PY'
class ActionEngine:

    def __init__(self):
        self.actions={}

    def register(self,name,callback):
        self.actions[name]=callback

    def execute(self,name):

        if name in self.actions:
            return self.actions[name]()

        return "Action not found"

engine=ActionEngine()
PY

cat > "$ROOT/backend/app/fred/actions/test.py" << 'PY'
from engine import engine

engine.register("hello",lambda:"Olá Bruno")
engine.register("status",lambda:"CBOS Online")
engine.register("fred",lambda:"FRED Ready")

print(engine.execute("hello"))
print(engine.execute("status"))
print(engine.execute("fred"))
print(engine.execute("teste"))
PY

echo
echo "[OK] Action Engine instalado."
echo
