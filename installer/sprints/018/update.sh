#!/usr/bin/env bash

ROOT="/opt/CasaBruno-Platform"

echo
echo "========================================"
echo "         SPRINT 018"
echo "========================================"
echo

echo "Instalando FastAPI..."

mkdir -p "$ROOT/backend/app/api"
mkdir -p "$ROOT/backend/app/api/routes"
mkdir -p "$ROOT/backend/app/api/controllers"
mkdir -p "$ROOT/backend/app/api/middlewares"

touch "$ROOT/backend/app/api/__init__.py"
touch "$ROOT/backend/app/api/routes/__init__.py"
touch "$ROOT/backend/app/api/controllers/__init__.py"
touch "$ROOT/backend/app/api/middlewares/__init__.py"

cat > "$ROOT/backend/app/api/main.py" << 'APP'
from fastapi import FastAPI

app = FastAPI(
    title="CBOS API",
    version="1.0.0"
)

@app.get("/")
def root():
    return {
        "platform":"CBOS",
        "ai":"FRED",
        "status":"online"
    }
APP

echo
echo "[OK] FastAPI instalada."
echo
