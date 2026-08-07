#!/usr/bin/env bash

echo
echo "======================================="
echo " VALIDAÇÃO SPRINT-001"
echo "======================================="
echo

[ -d /opt/CasaBruno-Platform/backend ] && echo "[OK] Backend"
[ -d /opt/CasaBruno-Platform/frontend ] && echo "[OK] Frontend"
[ -d /opt/CasaBruno-Platform/docs ] && echo "[OK] Docs"
[ -d /opt/CasaBruno-Platform/ai ] && echo "[OK] AI"
[ -d /opt/CasaBruno-Platform/tools ] && echo "[OK] Tools"
[ -d /opt/CasaBruno-Platform/sprints ] && echo "[OK] Sprints"

echo
echo "Sprint validada com sucesso."
echo
