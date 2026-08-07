#!/usr/bin/env bash

ROOT="/opt/CasaBruno-Platform"

echo
echo "========================================"
echo "         SPRINT 031"
echo "========================================"
echo

echo "Instalando Command Engine..."

mkdir -p "$ROOT/backend/app/fred/commands"

touch "$ROOT/backend/app/fred/commands/__init__.py"

cat > "$ROOT/backend/app/fred/commands/engine.py" << 'PY'
class CommandEngine:

    def __init__(self):
        self.commands={}

    def register(self,name,action):
        self.commands[name]=action

    def run(self,name):

        if name in self.commands:
            return self.commands[name]()

        return "Unknown command"

engine=CommandEngine()
PY

cat > "$ROOT/backend/app/fred/commands/test.py" << 'PY'
from engine import engine

engine.register("status",lambda:"System Online")
engine.register("docker",lambda:"Docker OK")
engine.register("ha",lambda:"Home Assistant OK")

print(engine.run("status"))
print(engine.run("docker"))
print(engine.run("ha"))
print(engine.run("teste"))
PY

echo
echo "[OK] Command Engine instalado."
echo
