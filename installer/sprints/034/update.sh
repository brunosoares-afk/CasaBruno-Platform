#!/usr/bin/env bash

ROOT="/opt/CasaBruno-Platform"

echo
echo "========================================"
echo "         SPRINT 034"
echo "========================================"
echo

echo "Instalando Session Manager..."

mkdir -p "$ROOT/backend/app/fred/session"

touch "$ROOT/backend/app/fred/session/__init__.py"

cat > "$ROOT/backend/app/fred/session/session.py" << 'PY'
class Session:

    def __init__(self):
        self.sessions={}

    def open(self,user):
        self.sessions[user]="active"

    def close(self,user):
        self.sessions[user]="closed"

    def status(self,user):
        return self.sessions.get(user)

    def list(self):
        return self.sessions

session=Session()
PY

cat > "$ROOT/backend/app/fred/session/test.py" << 'PY'
from session import session

session.open("Bruno")
session.open("CasaBruno")

print(session.status("Bruno"))

session.close("Bruno")

print(session.status("Bruno"))
print(session.list())
PY

echo
echo "[OK] Session Manager instalado."
echo
