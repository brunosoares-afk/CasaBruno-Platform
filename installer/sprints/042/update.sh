#!/usr/bin/env bash

ROOT="/opt/CasaBruno-Platform"

echo
echo "========================================"
echo "         SPRINT 042"
echo "========================================"
echo

echo "Instalando WebSocket Server..."

mkdir -p "$ROOT/backend/app/websocket"

touch "$ROOT/backend/app/websocket/__init__.py"

cat > "$ROOT/backend/app/websocket/server.py" << 'PY'
from fastapi import WebSocket

class WebSocketManager:

    def __init__(self):
        self.clients=[]

    async def connect(self,ws:WebSocket):
        await ws.accept()
        self.clients.append(ws)

    async def disconnect(self,ws:WebSocket):
        if ws in self.clients:
            self.clients.remove(ws)

    async def broadcast(self,message:str):
        for client in self.clients:
            await client.send_text(message)

manager=WebSocketManager()
PY

cat > "$ROOT/backend/app/websocket/test.py" << 'PY'
from server import manager

print("Clients:",len(manager.clients))
print("WebSocket Server Ready")
PY

echo
echo "[OK] WebSocket Server instalado."
echo
