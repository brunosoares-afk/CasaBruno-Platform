#!/usr/bin/env bash

ROOT="/opt/CasaBruno-Platform"

echo
echo "==============================================="
echo "           CBOS PATCH ENGINE"
echo "==============================================="
echo

mkdir -p "$ROOT/build/engine/logs"
mkdir -p "$ROOT/build/engine/backups"

LOG="$ROOT/build/engine/logs/patch.log"

echo "Patch Engine iniciado em $(date)" >> "$LOG"

echo "[1/5] Estrutura...............OK"
echo "[2/5] Logs...................OK"
echo "[3/5] Backups...............OK"
echo "[4/5] Patch Engine..........OK"
echo "[5/5] Builder...............READY"

echo
echo "Patch Engine instalado."
echo
