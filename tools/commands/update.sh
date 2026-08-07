#!/usr/bin/env bash

ROOT="/opt/CasaBruno-Platform"

source "$ROOT/tools/lib/colors.sh"
source "$ROOT/tools/lib/banner.sh"
source "$ROOT/tools/lib/logger.sh"

banner

echo
echo "Atualizando CBOS..."
echo

log "===== UPDATE ====="

cd "$ROOT" || exit 1

echo "[1/6] Git Pull"
git pull
log "Git Pull"

echo
echo "[2/6] Backend"

if [ -f backend/requirements.txt ]; then
    pip3 install -r backend/requirements.txt
fi

log "Backend atualizado"

echo
echo "[3/6] Frontend"

if [ -f frontend/package.json ]; then
    cd frontend || exit
    npm install
    cd ..
fi

log "Frontend atualizado"

echo
echo "[4/6] Docker"

docker compose pull

log "Docker Pull"

echo
echo "[5/6] Docker Compose"

docker compose up -d

log "Docker Restart"

echo
echo "[6/6] Finalizando"

echo

echo -e "${GREEN}Atualização concluída.${RESET}"

log "Update concluído"
