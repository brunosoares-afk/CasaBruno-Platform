#!/usr/bin/env bash

cd /opt/CasaBruno-Platform/backend/app

exec uvicorn api.main:app \
    --host 0.0.0.0 \
    --port 8080
