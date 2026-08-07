#!/usr/bin/env bash

echo
echo "========================================"
echo "         SPRINT 046"
echo "========================================"
echo

echo "Instalando Dashboard Live..."

systemctl restart cbos-api

sleep 2

echo
echo "[OK] Dashboard Live instalado."
echo

curl -s http://127.0.0.1:8080/api/status

echo
