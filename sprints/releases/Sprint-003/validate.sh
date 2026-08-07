#!/usr/bin/env bash

ROOT="/opt/CasaBruno-Platform"

echo
echo "========== PATCH ENGINE =========="
echo

test -d "$ROOT/build/engine" && echo "[OK] engine"
test -d "$ROOT/build/engine/logs" && echo "[OK] logs"
test -d "$ROOT/build/engine/backups" && echo "[OK] backups"

echo

echo "Patch Engine operacional."
