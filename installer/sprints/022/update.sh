#!/usr/bin/env bash

ROOT="/opt/CasaBruno-Platform"

echo
echo "========================================"
echo "         SPRINT 022"
echo "========================================"
echo

mkdir -p "$ROOT/backend/app/fred/memory"

cat > "$ROOT/backend/app/fred/memory/__init__.py" << 'PY'
PY

cat > "$ROOT/backend/app/fred/memory/memory.py" << 'PY'
class Memory:

    def __init__(self):
        self.data = {}

    def set(self,key,value):
        self.data[key]=value

    def get(self,key):
        return self.data.get(key)

    def all(self):
        return self.data

memory = Memory()
PY

cat > "$ROOT/backend/app/fred/memory/test.py" << 'PY'
from memory import memory

memory.set("user","Bruno")
memory.set("house","CasaBruno")

print(memory.get("user"))
print(memory.get("house"))
print(memory.all())
PY

echo
echo "[OK] Memory Engine instalado."
echo
