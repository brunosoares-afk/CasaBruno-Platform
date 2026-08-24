import asyncio
import logging
from datetime import datetime, timezone

from app.core.android.manager import android
from app.services import alexa_service, detection_service, presence_service, tuya_service

logger = logging.getLogger("ha_websocket_service")
logger.setLevel(logging.INFO)
if not logging.getLogger().handlers:
    logging.basicConfig(level=logging.INFO)

DETECTION_TICK_S = 5
TUYA_TICK_S = 5
PRESENCE_TICK_S = 20
BTV13_TICK_S = 15
ALEXA_TICK_S = 15

# Nome que o alexa-bridge devolve em GET /devices -> entity_id (mesmo
# padrão do _TUYA_ENTITIES acima).
_ALEXA_NAME_TO_ENTITY = {
    "Alexa Taiane": "media_player.alexa_taiane",
    "Bruno's N65B": "media_player.bruno_s_n65b",
}

# Esses entity_id são lidos só pelo _tuya_loop (polling local direto nos
# dispositivos) — mantido separado do que a HA expunha via Tuya Cloud
# pra não haver dois escritores do mesmo estado.
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


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _build_detection_entities() -> dict[str, dict]:
    """Monta as entidades sintéticas em cima de :8091 (rosto) e :8092
    (placa) — as 5 originais preservam o mesmo entity_id/formato que o HA
    produzia via platform: rest, pra nenhum consumidor do frontend
    precisar mudar; as 2 novas (pessoa/veículo, ver
    [[casa-bruno-yoosee-object-detection-2026-08-23]]) seguem o mesmo
    padrão de shape."""

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
        # Detecção geral de pessoa/veículo (YOLOv4-tiny), ver
        # [[casa-bruno-yoosee-object-detection-2026-08-23]] — mesmo /status
        # do plate-detect-yoosee, campos novos ao lado dos de sempre.
        entities["binary_sensor.yoosee_pessoa_detectada"] = {
            "entity_id": "binary_sensor.yoosee_pessoa_detectada",
            "state": "on" if plate.get("people_detected") else "off",
            "attributes": {
                "device_class": "occupancy",
                "count": plate.get("people_count", 0),
                "friendly_name": "Yoosee Pessoa Detectada",
            },
            "last_updated": now,
        }
        entities["sensor.yoosee_veiculos_detectados"] = {
            "entity_id": "sensor.yoosee_veiculos_detectados",
            "state": str(plate.get("vehicle_count", 0)),
            "attributes": {
                "vehicles": plate.get("vehicles", []),
                "plates_detected": plate.get("plates_detected", []),
                "friendly_name": "Yoosee Veículos Detectados",
            },
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


def _build_btv13_entity() -> dict[str, dict]:
    """binary_sensor.btv13_adb nativo — antes só existia como entidade do
    HA (checagem 'adb devices' rodando lá dentro), então o handler já
    pronto em automations_service.py nunca era chamado de verdade (não
    existe nenhum client de websocket real do HA nesse backend, só esses
    3-4 loops nativos). Reaproveita o mesmo android.list() que já
    alimenta /network/adb — mesmo shape de entidade que o HA expunha, pra
    o handler existente funcionar sem mudar nada nele."""
    now = _now_iso()
    for device in android.list():
        if device.get("id") == "btv13":
            return {
                "binary_sensor.btv13_adb": {
                    "entity_id": "binary_sensor.btv13_adb",
                    "state": "on" if device.get("status") == "online" else "off",
                    "attributes": {"device_class": "connectivity", "friendly_name": "BTV13 ADB"},
                    "last_updated": now,
                }
            }
    return {}


async def _btv13_loop() -> None:
    while True:
        try:
            entities = await asyncio.to_thread(_build_btv13_entity)
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
            logger.exception("Falha no loop de ADB do BTV13")

        await asyncio.sleep(BTV13_TICK_S)


def _build_alexa_entities() -> dict[str, dict]:
    """media_player.alexa_taiane/bruno_s_n65b nativos — mesma história do
    BTV13: eram só entidades da HA, sem HA não existem mais em lugar
    nenhum, mesmo o alexa-bridge já sabendo o status real (GET /devices)
    há tempos. Fica '—' na tela até isso alimentar o snapshot."""
    now = _now_iso()
    entities: dict[str, dict] = {}
    for device in alexa_service.devices().values():
        entity_id = _ALEXA_NAME_TO_ENTITY.get(device.get("name"))
        if not entity_id:
            continue
        entities[entity_id] = {
            "entity_id": entity_id,
            "state": "idle" if device.get("online") else "unavailable",
            "attributes": {"friendly_name": device.get("name")},
            "last_updated": now,
        }
    return entities


async def _alexa_loop() -> None:
    while True:
        try:
            entities = await asyncio.to_thread(_build_alexa_entities)
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
            logger.exception("Falha no loop da Alexa")

        await asyncio.sleep(ALEXA_TICK_S)


def start_ha_websocket_relay():
    asyncio.create_task(_detection_loop())
    asyncio.create_task(_tuya_loop())
    asyncio.create_task(_presence_loop())
    asyncio.create_task(_btv13_loop())
    asyncio.create_task(_alexa_loop())
