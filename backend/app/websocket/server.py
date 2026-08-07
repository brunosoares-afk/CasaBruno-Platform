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
