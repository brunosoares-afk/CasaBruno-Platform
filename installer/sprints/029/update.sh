#!/usr/bin/env bash

ROOT="/opt/CasaBruno-Platform"

echo
echo "========================================"
echo "         SPRINT 029"
echo "========================================"
echo

echo "Instalando Skill Engine..."

mkdir -p "$ROOT/backend/app/fred/skills"

touch "$ROOT/backend/app/fred/skills/__init__.py"

cat > "$ROOT/backend/app/fred/skills/engine.py" << 'PY'
class SkillEngine:

    def __init__(self):
        self.skills={}

    def register(self,name,description):
        self.skills[name]=description

    def list(self):
        return self.skills

engine=SkillEngine()
PY

cat > "$ROOT/backend/app/fred/skills/test.py" << 'PY'
from engine import engine

engine.register("homeassistant","Controle do Home Assistant")
engine.register("docker","Gerenciamento Docker")
engine.register("network","Monitoramento de Rede")

print(engine.list())
PY

echo
echo "[OK] Skill Engine instalado."
echo
