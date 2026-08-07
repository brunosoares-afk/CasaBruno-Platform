#!/usr/bin/env bash

ROOT="/opt/CasaBruno-Platform"

REL="$ROOT/releases/Release-1.0"

echo
echo "========================================="
echo "        CBOS RELEASE BUILDER"
echo "========================================="
echo

mkdir -p "$REL/output"

tar \
-czpf \
"$REL/output/Release-1.0.cbos" \
-C "$ROOT" \
backend \
frontend \
ai \
docs \
tools \
build \
sprints \
docker-compose.yml \
README.md

echo

echo "[OK] Pacote criado"

echo

ls -lh "$REL/output/Release-1.0.cbos"

echo
