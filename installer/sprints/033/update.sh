#!/usr/bin/env bash

ROOT="/opt/CasaBruno-Platform"

echo
echo "========================================"
echo "         SPRINT 033"
echo "========================================"
echo

echo "Instalando Context Engine..."

mkdir -p "$ROOT/backend/app/fred/context"

touch "$ROOT/backend/app/fred/context/__init__.py"

cat > "$ROOT/backend/app/fred/context/context.py" << 'PY'
class Context:

    def __init__(self):
        self.context={}

    def set(self,key,value):
        self.context[key]=value

    def get(self,key):
        return self.context.get(key)

    def dump(self):
        return self.context

context=Context()
PY

cat > "$ROOT/backend/app/fred/context/test.py" << 'PY'
from context import context

context.set("user","Bruno")
context.set("location","Casa")
context.set("mode","automation")

print(context.get("user"))
print(context.dump())
PY

echo
echo "[OK] Context Engine instalado."
echo
