#!/usr/bin/env bash

ROOT="/opt/CasaBruno-Platform"

echo
echo "========================================"
echo "         SPRINT 032"
echo "========================================"
echo

echo "Instalando AI Pipeline..."

mkdir -p "$ROOT/backend/app/fred/pipeline"

touch "$ROOT/backend/app/fred/pipeline/__init__.py"

cat > "$ROOT/backend/app/fred/pipeline/pipeline.py" << 'PY'
class Pipeline:

    def __init__(self):
        self.steps=[]

    def add(self,name):
        self.steps.append(name)

    def execute(self):
        return self.steps

pipeline=Pipeline()
PY

cat > "$ROOT/backend/app/fred/pipeline/test.py" << 'PY'
from pipeline import pipeline

pipeline.add("intent")
pipeline.add("router")
pipeline.add("skills")
pipeline.add("actions")

print(pipeline.execute())
PY

echo
echo "[OK] AI Pipeline instalado."
echo
