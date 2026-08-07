#!/usr/bin/env bash

ROOT="/opt/CasaBruno-Platform"

echo
echo "========================================"
echo "         SPRINT 025"
echo "========================================"
echo

echo "Instalando Docker Connector..."

mkdir -p "$ROOT/backend/app/fred/docker"

touch "$ROOT/backend/app/fred/docker/__init__.py"

cat > "$ROOT/backend/app/fred/docker/client.py" << 'PY'
import subprocess

class DockerClient:

    def containers(self):

        try:
            out=subprocess.check_output(
                ["docker","ps","--format","{{.Names}}"],
                text=True
            )
            return out.strip().splitlines()

        except Exception:
            return []

docker=DockerClient()
PY

cat > "$ROOT/backend/app/fred/docker/test.py" << 'PY'
from client import docker

print(docker.containers())
PY

echo
echo "[OK] Docker Connector instalado."
echo
