import json
import time

import websocket

from app.core.config.config import config

# area_registry/entity_registry/device_registry só existem via WebSocket do
# HA (confirmado: /api/config/area_registry via REST devolve 404) — não tem
# como fazer isso com o HomeAssistantClient (requests/REST) já existente.
# Muda raramente, então cacheia por alguns minutos em vez de abrir uma
# conexão WebSocket nova a cada requisição.
CACHE_TTL_SECONDS = 300


class HomeAssistantRegistry:

    def __init__(self):
        self._cache = None
        self._cached_at = 0

    def _config(self):
        cfg = config.get("homeassistant")
        host = cfg.get("host", "127.0.0.1")
        port = cfg.get("port", 8123)
        ssl = cfg.get("ssl", False)
        token = cfg.get("token", "")
        protocol = "wss" if ssl else "ws"
        return f"{protocol}://{host}:{port}/api/websocket", token

    def _fetch_raw(self):
        url, token = self._config()
        ws = websocket.create_connection(url, timeout=10)

        try:
            ws.recv()  # auth_required

            ws.send(json.dumps({"type": "auth", "access_token": token}))
            auth_result = json.loads(ws.recv())

            if auth_result.get("type") != "auth_ok":
                raise RuntimeError("Falha na autenticação WebSocket do Home Assistant")

            results = {}
            commands = [
                ("areas", "config/area_registry/list"),
                ("entities", "config/entity_registry/list"),
                ("devices", "config/device_registry/list"),
            ]

            for i, (key, cmd_type) in enumerate(commands, start=1):
                ws.send(json.dumps({"id": i, "type": cmd_type}))
                response = json.loads(ws.recv())
                results[key] = response.get("result", [])

            return results
        finally:
            ws.close()

    def areas_with_entities(self, force=False):
        now = time.time()

        if not force and self._cache is not None and (now - self._cached_at) < CACHE_TTL_SECONDS:
            return self._cache

        raw = self._fetch_raw()

        device_area = {d["id"]: d.get("area_id") for d in raw["devices"]}
        area_names = {a["area_id"]: a["name"] for a in raw["areas"]}

        grouped = {}
        for e in raw["entities"]:
            # entity_category "diagnostic"/"config" e disabled_by são
            # entidades internas de integração (ex: "_pre_release", sensores
            # de update) — não fazem sentido numa visão por área.
            if e.get("entity_category") or e.get("disabled_by"):
                continue

            area_id = e.get("area_id") or device_area.get(e.get("device_id"))
            if not area_id:
                continue
            grouped.setdefault(area_id, []).append(e["entity_id"])

        result = [
            {
                "area_id": area_id,
                "name": area_names.get(area_id, area_id),
                "entity_ids": entity_ids,
            }
            for area_id, entity_ids in grouped.items()
        ]

        self._cache = result
        self._cached_at = now
        return result


registry = HomeAssistantRegistry()
