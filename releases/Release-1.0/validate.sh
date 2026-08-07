#!/usr/bin/env bash

ROOT="/opt/CasaBruno-Platform"

echo
echo "========== RELEASE VALIDATION =========="
echo

items=(
backend
frontend
ai
docs
tools
sprints
build
releases
)

for item in "${items[@]}"
do
if [ -d "$ROOT/$item" ]; then
echo "[OK] $item"
else
echo "[FAIL] $item"
fi
done

echo
echo "Release validada."
echo
