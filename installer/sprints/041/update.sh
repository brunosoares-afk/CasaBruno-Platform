#!/usr/bin/env bash

ROOT="/opt/CasaBruno-Platform"

echo
echo "========================================"
echo "         SPRINT 041"
echo "========================================"
echo

echo "Instalando API Service..."

mkdir -p "$ROOT/backend/service"

cat > "$ROOT/backend/service/api-service.sh" << 'SH'
#!/usr/bin/env bash

cd /opt/CasaBruno-Platform/backend/app

exec uvicorn api.main:app \
    --host 0.0.0.0 \
    --port 8080
SH

chmod +x "$ROOT/backend/service/api-service.sh"

cat > /etc/systemd/system/cbos-api.service << 'SERVICE'
[Unit]
Description=CBOS API
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/CasaBruno-Platform/backend/app
ExecStart=/opt/CasaBruno-Platform/backend/service/api-service.sh
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
SERVICE

systemctl daemon-reload
systemctl enable cbos-api
systemctl restart cbos-api

echo
echo "[OK] API Service instalado."
echo
