#!/usr/bin/env bash

ROOT="/opt/CasaBruno-Platform"

echo

echo "========== BUILD VALIDATION =========="

echo

dirs=(
build
build/cache
build/packages
build/releases
build/tmp
)

for dir in "${dirs[@]}"
do

if [ -d "$ROOT/$dir" ]; then

echo "[OK] $dir"

else

echo "[FAIL] $dir"

fi

done

echo

echo "Validation finished."

echo
