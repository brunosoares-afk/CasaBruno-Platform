import asyncio
import json
import logging
from datetime import datetime, timezone

import websockets

from app.core.homeassistant.client import ha_client
from app.services import detection_service, presence_service, tuya_service

logger = logging.getLogger("ha_websocket_service")
logger.setLevel(logging.INFO)
if not logging.getLogger().handlers:
    logging.basicConfig(level=logging.INFO)

RECONNECT_DELAY_S = 5
MAX_RECONNECT_DELAY_S = 120
DETECTION_TICK_S = 5
TUYA_TICK_S = 5
PRESENCE_TICK_S = 20

# Esses entity_id passam a ser lidos só pelo _tuya_loop (polling local direto
# nos dispositivos) — o HA também tem a integração Tuya Cloud rodando pra
# eles, então o _relay_loop ignora os eventos state_changed que chegam do HA
# pra esses IDs, senão os dois ficariam brigando pra escrever o mesmo estado.
TUYA_MANAGED_ENTITY_IDS = tuya_service.MANAGED_ENTITY_IDS

# Mesma ideia, pra presença de rede (leases do MikroTik) em vez do app
# companion da HA (mobile_app) — 2026-08-16, ver [[casa-bruno-migracao-ha-roadmap]].
PRESENCE_MANAGED_ENTITY_IDS = set(presence_service.MAC_TO_ENTITY.values())

# Snapshot completo em memória, mantido em sincronia pelos eventos
# state_changed — mesmo padrão simples já usado em outros lugares desse
# backend (_sessions em auth.py, _packet_loss_samples em network.py):
# um dict/set de processo, sem fila/broker novo.
_snapshot_by_id: dict[str, dict] = {}
_clients: set = set()

# Assinantes internos (mesmo processo) de cada mudança de estado — usado
# pelo automations_service pra reagir sem precisar de um segundo WebSocket
# cliente-de-si-mesmo. Separado de _clients porque esses callbacks são
# funções Python, não sockets de navegador.
_internal_listeners: list = []


def get_snapshot() -> list[dict]:
    return list(_snapshot_by_id.values())


def register_client(ws) -> None:
    _clients.add(ws)


def unregister_client(ws) -> None:
    _clients.discard(ws)


def subscribe(callback) -> None:
    _internal_listeners.append(callback)


async def _broadcast(message: dict) -> None:
    for cb in _internal_listeners:
        try:
            await cb(message)
        except Exception:
            logger.exception("Falha em listener interno de state_changed")

    if not _clients:
        return
    dead = []
    for client in _clients:
        try:
            await client.send_json(message)
        except Exception:
            dead.append(client)
    for client in dead:
        _clients.discard(client)


def _ws_url() -> str:
    protocol = "wss" if ha_client.ssl else "ws"
    return f"{protocol}://{ha_client.host}:{ha_client.port}/api/websocket"


async def _load_initial_snapshot() -> None:
    try:
        states = await asyncio.to_thread(ha_client.states)

        # Preserva os valores sintéticos (Tuya/presença) que já estavam no
        # snapshot em vez de limpar tudo — sem isso, toda reconexão do
        # relay (comum, ver RECONNECT_DELAY_S) reintroduzia por um instante
        # o valor cru da HA pra esses entity_id (ex: person.taiane sempre
        # "unknown" na HA de verdade, nunca teve tracker configurado lá)
        # até o próximo tick do loop correspondente corrigir — pra Tuya
        # (5s) passava despercebido, pra presença (20s) já dava pra ver
        # "Desconhecido" na tela. Reproduzido ao vivo 2026-08-16.
        managed = TUYA_MANAGED_ENTITY_IDS | PRESENCE_MANAGED_ENTITY_IDS
        preserved = {k: v for k, v in _snapshot_by_id.items() if k in managed}

        _snapshot_by_id.clear()
        for entity in states:
            if entity["entity_id"] not in managed:
                _snapshot_by_id[entity["entity_id"]] = entity
        _snapshot_by_id.update(preserved)

        logger.info("Snapshot inicial carregado: %d entidades", len(_snapshot_by_id))
    except Exception as exc:
        logger.warning("Falha ao carregar snapshot inicial do HA: %s", exc)


async def _relay_loop() -> None:
    delay = RECONNECT_DELAY_S
    while True:
        try:
            await _load_initial_snapshot()
            await _broadcast({"type": "snapshot", "states": get_snapshot()})

            async with websockets.connect(_ws_url(), open_timeout=10) as ws:

                first = json.loads(await ws.recv())
                if first.get("type") != "auth_required":
                    raise RuntimeError(f"Handshake inesperado do HA: {first}")

                await ws.send(json.dumps({"type": "auth", "access_token": ha_client.token}))
                auth_result = json.loads(await ws.recv())
                if auth_result.get("type") != "auth_ok":
                    raise RuntimeError(f"Falha de autenticação no WS do HA: {auth_result}")

                await ws.send(json.dumps({
                    "id": 1,
                    "type": "subscribe_events",
                    "event_type": "state_changed",
                }))
                ack = json.loads(await ws.recv())
                if not ack.get("success", True):
                    raise RuntimeError(f"Falha ao assinar state_changed: {ack}")

                logger.info("Conectado ao WebSocket do HA, ouvindo state_changed")
                delay = RECONNECT_DELAY_S

                async for raw in ws:
                    msg = json.loads(raw)
                    if msg.get("type") != "event":
                        continue

                    data = msg.get("event", {}).get("data", {})
                    new_state = data.get("new_state")
                    entity_id = data.get("entity_id")

                    if not entity_id:
                        continue

                    if entity_id in TUYA_MANAGED_ENTITY_IDS:
                        # Fonte da verdade pra esses IDs é o _tuya_loop (polling
                        # local), não o HA (que também escuta a Tuya Cloud).
                        continue

                    if entity_id in PRESENCE_MANAGED_ENTITY_IDS:
                        # Fonte da verdade agora é o _presence_loop (leases do
                        # MikroTik), não o app companion da HA (mobile_app).
                        continue

                    if new_state is None:
                        _snapshot_by_id.pop(entity_id, None)
                    else:
                        _snapshot_by_id[entity_id] = new_state

                    await _broadcast({
                        "type": "state_changed",
                        "entity_id": entity_id,
                        "new_state": new_state,
                    })

        except Exception as exc:
            # HA Core está desligado de propósito desde 2026-08-16 (migração
            # em andamento) — logger.exception() aqui gerava um traceback
            # completo a cada 5s (>1000/h) só de "connection refused",
            # enterrando erros reais no log. Backoff exponencial + uma linha
            # concisa em vez de stack trace.
            logger.warning(
                "Conexão com o WS do HA caiu (%s), tentando de novo em %ds",
                exc, delay,
            )
            await asyncio.sleep(delay)
            delay = min(delay * 2, MAX_RECONNECT_DELAY_S)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _build_detection_entities() -> dict[str, dict]:
    """Monta as mesmas 5 entidades que o HA produzia via platform: rest
    em cima de :8091 (rosto) e :8092 (placa) — mesmo entity_id, mesmo
    formato de state/attributes, pra nenhum consumidor do frontend
    precisar mudar."""

    face = detection_service.get_face_status()
    plate = detection_service.get_plate_status()
    now = _now_iso()
    entities: dict[str, dict] = {}

    if face is not None:
        entities["sensor.icsee_rostos_detectados"] = {
            "entity_id": "sensor.icsee_rostos_detectados",
            "state": str(face.get("face_count", 0)),
            "attributes": {
                "camera_online": face.get("camera_online"),
                "last_check": face.get("last_check"),
                "last_success": face.get("last_success"),
                "friendly_name": "iCSee Rostos Detectados",
            },
            "last_updated": now,
        }
        entities["sensor.icsee_pessoa_reconhecida"] = {
            "entity_id": "sensor.icsee_pessoa_reconhecida",
            "state": detection_service.recognized_person_name(face),
            "attributes": {
                "recognized": face.get("recognized"),
                "face_count": face.get("face_count"),
                "friendly_name": "iCSee Pessoa Reconhecida",
            },
            "last_updated": now,
        }
        entities["binary_sensor.icsee_rosto_detectado"] = {
            "entity_id": "binary_sensor.icsee_rosto_detectado",
            "state": "on" if face.get("faces_detected") else "off",
            "attributes": {
                "device_class": "occupancy",
                "friendly_name": "iCSee Rosto Detectado",
            },
            "last_updated": now,
        }

    if plate is not None:
        entities["sensor.yoosee_placa_detectada"] = {
            "entity_id": "sensor.yoosee_placa_detectada",
            "state": plate.get("last_text") or "Nenhuma",
            "attributes": {
                "camera_online": plate.get("camera_online"),
                "matched_target": plate.get("matched_target"),
                "last_match": plate.get("last_match"),
                "friendly_name": "Yoosee Placa Detectada",
            },
            "last_updated": now,
        }
        entities["binary_sensor.yoosee_placa_alvo_detectada"] = {
            "entity_id": "binary_sensor.yoosee_placa_alvo_detectada",
            "state": "on" if plate.get("matched_target") else "off",
            "attributes": {"friendly_name": "Yoosee Placa Alvo Detectada"},
            "last_updated": now,
        }

    return entities


async def _detection_loop() -> None:
    while True:
        try:
            entities = await asyncio.to_thread(_build_detection_entities)
            for entity_id, new_state in entities.items():
                old = _snapshot_by_id.get(entity_id)
                _snapshot_by_id[entity_id] = new_state
                changed = (
                    old is None
                    or old.get("state") != new_state.get("state")
                    or old.get("attributes") != new_state.get("attributes")
                )
                if changed:
                    await _broadcast({
                        "type": "state_changed",
                        "entity_id": entity_id,
                        "new_state": new_state,
                    })
        except Exception:
            logger.exception("Falha no loop de detecção (rosto/placa)")

        await asyncio.sleep(DETECTION_TICK_S)


# entity_id -> (device_key, friendly_name, attributes extra) — mesmo shape
# que o HA já expunha pra esses 3 entity_id (visto direto via /states antes
# da troca), pra nenhum consumidor do frontend precisar mudar.
_TUYA_ENTITIES = {
    "light.lampada_cozinha": (
        "lampada_cozinha",
        {
            "supported_color_modes": ["onoff"],
            "color_mode": None,
            "friendly_name": "Lâmpada Cozinha",
            "supported_features": 0,
        },
    ),
    "switch.lampada_cozinha_switch_1": (
        "lampada_cozinha",
        {"device_class": "outlet", "friendly_name": "lâmpada cozinha Switch 1"},
    ),
    "switch.portao_casa_switch_1": (
        "portao",
        {"device_class": "outlet", "friendly_name": "portão casa Switch 1"},
    ),
}


def _build_tuya_entities() -> dict[str, dict]:
    now = _now_iso()
    status_by_device: dict[str, bool | None] = {}
    entities: dict[str, dict] = {}

    for entity_id, (device_key, attributes) in _TUYA_ENTITIES.items():
        if device_key not in status_by_device:
            status_by_device[device_key] = tuya_service.get_status(device_key)
        is_on = status_by_device[device_key]

        if is_on is None:
            continue

        entities[entity_id] = {
            "entity_id": entity_id,
            "state": "on" if is_on else "off",
            "attributes": attributes,
            "last_updated": now,
        }

    return entities


async def _tuya_loop() -> None:
    while True:
        try:
            entities = await asyncio.to_thread(_build_tuya_entities)
            for entity_id, new_state in entities.items():
                old = _snapshot_by_id.get(entity_id)
                _snapshot_by_id[entity_id] = new_state
                changed = old is None or old.get("state") != new_state.get("state")
                if changed:
                    await _broadcast({
                        "type": "state_changed",
                        "entity_id": entity_id,
                        "new_state": new_state,
                    })
        except Exception:
            logger.exception("Falha no loop de Tuya local (lâmpada/portão)")

        await asyncio.sleep(TUYA_TICK_S)


def _build_presence_entities() -> dict[str, dict]:
    now = _now_iso()
    entities: dict[str, dict] = {}

    for entity_id, state in presence_service.get_presence().items():
        entities[entity_id] = {
            "entity_id": entity_id,
            "state": state,
            "attributes": {"friendly_name": presence_service.FRIENDLY_NAME.get(entity_id, entity_id)},
            "last_updated": now,
        }

    return entities


async def _presence_loop() -> None:
    while True:
        try:
            entities = await asyncio.to_thread(_build_presence_entities)
            for entity_id, new_state in entities.items():
                old = _snapshot_by_id.get(entity_id)
                _snapshot_by_id[entity_id] = new_state
                changed = old is None or old.get("state") != new_state.get("state")
                if changed:
                    await _broadcast({
                        "type": "state_changed",
                        "entity_id": entity_id,
                        "new_state": new_state,
                    })
        except Exception:
            logger.exception("Falha no loop de presença (leases do MikroTik)")

        await asyncio.sleep(PRESENCE_TICK_S)


def start_ha_websocket_relay():
    asyncio.create_task(_relay_loop())
    asyncio.create_task(_detection_loop())
    asyncio.create_task(_tuya_loop())
    asyncio.create_task(_presence_loop())
