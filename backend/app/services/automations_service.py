import asyncio
import logging
from datetime import datetime, timezone

from app.core.homeassistant.client import ha_client
from app.services import ha_websocket_service, homeassistant_service, notify_service

logger = logging.getLogger("automations_service")
logger.setLevel(logging.INFO)
if not logging.getLogger().handlers:
    logging.basicConfig(level=logging.INFO)

# Portas das 10 automações que moravam em automations.yaml — os ids
# originais viram comentário em cada função, só pra rastrear de volta ao
# YAML. Sem framework genérico: cada automação é o corpo de uma função,
# igual o resto desse backend já faz (automation_engine.py, scheduler_service.py).

TICK_SECONDS = 60

# Fase 8 — contagem de erro real das automações, pra "como está a casa"
# poder responder "nenhuma automação apresentou erro" (ou não). As
# automações rodam soltas via asyncio.create_task, então uma exceção
# dentro delas normalmente só vira um "Task exception was never
# retrieved" no log e mais nada — _run_tracked() é o que garante que
# isso também incrementa esse contador, não só loga.
_automation_errors = {"count": 0, "last_message": None, "last_at": None}


async def _run_tracked(coro):
    try:
        await coro
    except Exception as error:
        logger.exception("Falha numa automação")
        _automation_errors["count"] += 1
        _automation_errors["last_message"] = str(error)
        _automation_errors["last_at"] = datetime.now(timezone.utc).isoformat()


def get_automation_error_count() -> int:
    return _automation_errors["count"]

MOBILE_APP_SERVICE = "mobile_app_poco_x8"

PERSON_ENTITIES = ("person.casa_inteligente", "person.taiane")

# Último estado completo conhecido por entity_id — semeado pelo snapshot
# inicial que o _relay_loop já manda, depois mantido pelos state_changed.
_last_state: dict[str, dict] = {}

# Cooldowns (substituem os input_boolean.*_cooldown de antes — nenhum
# consumidor do frontend lia esses input_boolean, seguro virar memória).
_cooldowns: dict[str, bool] = {}

# Flags diários (substituem input_boolean.bom_dia_executado_hoje /
# conversa_taiane_executada_hoje — as duas automações reset_* viram só
# esse dict + o tick abaixo, não automações à parte).
_daily_flags = {
    "bom_dia_executado_hoje": False,
    "conversa_taiane_executada_hoje": False,
}
_daily_reset_last_date: dict[str, str] = {}

# Tasks pendentes de debounce "for" — uma por automação-chave, cancelada
# se o estado sair do valor esperado antes do tempo (mesmo comportamento
# do "for" do HA: sair do estado antes da hora cancela o gatilho).
_pending_for: dict[str, asyncio.Task] = {}


def _cancel_for(key: str) -> None:
    task = _pending_for.get(key)
    if task and not task.done():
        task.cancel()


def _schedule_for(key: str, seconds: float, handler, state: dict) -> None:
    _cancel_for(key)

    async def _wait():
        try:
            await asyncio.sleep(seconds)
        except asyncio.CancelledError:
            return
        await _run_tracked(handler(state))

    _pending_for[key] = asyncio.create_task(_wait())


def _start_cooldown(key: str, seconds: float) -> None:
    _cooldowns[key] = True

    async def _clear():
        await asyncio.sleep(seconds)
        _cooldowns[key] = False

    asyncio.create_task(_clear())


def _in_cooldown(key: str) -> bool:
    return _cooldowns.get(key, False)


def _state_of(entity_id: str) -> str | None:
    entity = _last_state.get(entity_id)
    return entity.get("state") if entity else None


# ==========================================================
# AÇÕES REUTILIZÁVEIS (todas bloqueantes por baixo — chamadas
# via asyncio.to_thread, mesmo padrão do _weather_job em scheduler_service.py)
# ==========================================================

async def _call_device(domain: str, service: str, entity_id: str):
    """switch.lampada_cozinha_switch_1 / switch.portao_casa_switch_1 — já
    passa pela interceptação Tuya da Fase 2, sem duplicar nada aqui."""
    return await asyncio.to_thread(homeassistant_service.call_service, domain, service, entity_id)


async def _call_ha(domain: str, service: str, data: dict):
    """Ações que só o HA sabe fazer hoje (Alexa, push do app companion) —
    migrar a automação não exige parar de usar o HA pra essas."""
    return await asyncio.to_thread(ha_client.call_service, domain, service, data)


async def _push(title: str, message: str):
    await _call_ha("notify", MOBILE_APP_SERVICE, {"title": title, "message": message})


async def _announce(message: str):
    """Antes falava pela Alexa (notify.alexa_taiane_speak) — abandonado
    junto com a integração Alexa (Fase 5, ver [[casa-bruno-ha-removal-phases-4-6]]),
    agora avisa por WhatsApp (texto + voz) via notify_service, mesmo
    caminho já usado pelos avisos proativos do scheduler_service."""
    await notify_service.notify(message)


# ==========================================================
# 1. presenca_chegada_liga_luz — Fase 7: só depois das 18h (chegar de
# manhã/tarde não precisa de luz nem saudação), e agora manda boas-vindas
# por WhatsApp em vez de só ligar a luz. Deliberadamente NÃO mexe no
# portão aqui — decisão de escopo explícita do usuário, ver
# [[casa-bruno-fase7-automacoes-inteligentes]]: abrir o portão sozinho
# por presença já causou um incidente de segurança antes.
# ==========================================================

async def _presenca_chegada_liga_luz(entity_id: str, new_state: dict):
    hour = datetime.now(timezone.utc).astimezone().hour
    if hour < 18:
        return

    await _call_device("switch", "turn_on", "switch.lampada_cozinha_switch_1")
    # Mensagem de boas-vindas desativada a pedido do usuário 2026-08-16 —
    # luz continua acendendo, só o aviso por WhatsApp foi tirado (mesma
    # decisão aplicada em _chegada_reconhecimento_facial acima).


# ==========================================================
# 2. seguranca_desconhecido_casa_vazia (for 10s)
# ==========================================================

async def _seguranca_desconhecido_casa_vazia(new_state: dict):
    if any(_state_of(p) != "not_home" for p in PERSON_ENTITIES):
        return

    await _push(
        "⚠️ Rosto desconhecido detectado",
        "A câmera da sala reconheceu alguém não cadastrado, e ninguém da família está em casa.",
    )
    await notify_service.notify(
        "Atenção: a câmera da sala reconheceu um rosto desconhecido e ninguém da família está em casa."
    )


# ==========================================================
# 5. rotina_bom_dia_reconhecimento_facial
# ==========================================================

async def _rotina_bom_dia(new_state: dict):
    hour = datetime.now(timezone.utc).astimezone().hour
    if not (6 <= hour < 8) or _daily_flags["bom_dia_executado_hoje"]:
        return

    _daily_flags["bom_dia_executado_hoje"] = True
    await _announce("Bom dia! Tudo bem? Como foi sua noite?")


# ==========================================================
# 6. rotina_conversa_taiane_reconhecimento_facial
# ==========================================================

async def _rotina_conversa_taiane(new_state: dict):
    if _daily_flags["conversa_taiane_executada_hoje"]:
        return

    _daily_flags["conversa_taiane_executada_hoje"] = True
    await _announce("Oi Taiane! Como foi seu dia? Aconteceu algo especial?")


# ==========================================================
# 7. placa_ovi8d97_abre_portao
# ==========================================================

async def _placa_abre_portao(new_state: dict):
    if _in_cooldown("portao_placa"):
        return

    _start_cooldown("portao_placa", 5 * 60)
    await _push(
        "🚗 Placa OVI8D97 reconhecida",
        "A câmera Yoosee reconheceu o carro preto OVI8D97. Abrindo o portão.",
    )
    await notify_service.notify(
        "Placa OVI8D97 reconhecida pela câmera Yoosee. Abrindo o portão."
    )

    result = await _call_device("switch", "turn_on", "switch.portao_casa_switch_1")
    if not result.get("success"):
        await _push(
            "⚠️ Não consegui abrir o portão",
            "Placa OVI8D97 reconhecida, mas o comando local pro portão falhou.",
        )


# ==========================================================
# 8. chegada_por_reconhecimento_facial (for 5s)
# ==========================================================
# Mensagem "X chegou em casa" desativada a pedido do usuário 2026-08-16
# — luz da cozinha continua acendendo na chegada, só o aviso por
# WhatsApp foi tirado.

async def _chegada_reconhecimento_facial(new_state: dict):
    if _in_cooldown("reconhecimento_facial"):
        return

    _start_cooldown("reconhecimento_facial", 15 * 60)
    await _call_device("switch", "turn_on", "switch.lampada_cozinha_switch_1")


# ==========================================================
# 9. btv13_perdeu_conexao_adb (for 2min)
# ==========================================================

async def _btv13_perdeu_adb(new_state: dict):
    await _push(
        "📺 BTV13 perdeu a conexão ADB",
        "A porta 5555 caiu de novo (depuração de rede desligada). Precisa reativar manualmente na tela da TV — não tem como resolver remotamente.",
    )
    await notify_service.notify(
        "O BTV13 perdeu a conexão ADB de novo. Precisa reativar manualmente na tela da TV."
    )


# ==========================================================
# 10. saude_batimento_cardiaco_elevado (numeric, for 20s)
# ==========================================================

async def _batimento_elevado(new_state: dict):
    if _in_cooldown("batimento_alerta"):
        return

    _start_cooldown("batimento_alerta", 10 * 60)
    bpm = new_state.get("state")
    await _push(
        "❤️ Batimento cardíaco elevado",
        f"Seu relógio registrou {bpm} bpm, acima do limite de 120.",
    )


# ==========================================================
# DISPATCH — recebe todo state_changed, decide quais das 10
# automações reagem a cada entity_id
# ==========================================================

def _on_person_changed(entity_id: str, old_state: str | None, new_state: dict):
    if old_state == "not_home" and new_state.get("state") == "home":
        asyncio.create_task(_run_tracked(_presenca_chegada_liga_luz(entity_id, new_state)))


def _on_pessoa_reconhecida_changed(entity_id: str, old_state: str | None, new_state: dict):
    state = new_state.get("state")

    if state == "Desconhecido":
        _schedule_for("seguranca_desconhecido", 10, _seguranca_desconhecido_casa_vazia, new_state)
    else:
        _cancel_for("seguranca_desconhecido")

    if state in ("Bruno", "Taiane"):
        asyncio.create_task(_run_tracked(_rotina_bom_dia(new_state)))
        if state == "Taiane":
            asyncio.create_task(_run_tracked(_rotina_conversa_taiane(new_state)))
        _schedule_for("chegada_reconhecimento", 5, _chegada_reconhecimento_facial, new_state)
    else:
        _cancel_for("chegada_reconhecimento")


def _on_placa_alvo_changed(entity_id: str, old_state: str | None, new_state: dict):
    if new_state.get("state") == "on":
        asyncio.create_task(_run_tracked(_placa_abre_portao(new_state)))


def _on_btv13_adb_changed(entity_id: str, old_state: str | None, new_state: dict):
    if new_state.get("state") == "off":
        _schedule_for("btv13_adb", 2 * 60, _btv13_perdeu_adb, new_state)
    else:
        _cancel_for("btv13_adb")


def _on_heart_rate_changed(entity_id: str, old_state: str | None, new_state: dict):
    try:
        value = float(new_state.get("state"))
    except (TypeError, ValueError):
        return

    if value > 120:
        _schedule_for("batimento_elevado", 20, _batimento_elevado, new_state)
    else:
        _cancel_for("batimento_elevado")


_ENTITY_HANDLERS = {
    "person.casa_inteligente": _on_person_changed,
    "person.taiane": _on_person_changed,
    "sensor.icsee_pessoa_reconhecida": _on_pessoa_reconhecida_changed,
    "binary_sensor.yoosee_placa_alvo_detectada": _on_placa_alvo_changed,
    "binary_sensor.btv13_adb": _on_btv13_adb_changed,
    "sensor.poco_x8_heart_rate": _on_heart_rate_changed,
}


# _last_state só guarda os ~6 entity_id acima — não é um segundo espelho
# do snapshot inteiro (esse já existe em ha_websocket_service). Precisa
# existir separado porque, quando esse listener roda, o snapshot global
# JÁ foi sobrescrito com o novo valor (os loops escrevem em _snapshot_by_id
# antes de chamar _broadcast) — sem isso não daria pra detectar from/to.
_TRACKED_ENTITY_IDS = set(_ENTITY_HANDLERS.keys())


async def _on_ws_message(message: dict) -> None:
    msg_type = message.get("type")

    if msg_type == "snapshot":
        for state in message.get("states", []):
            entity_id = state.get("entity_id")
            if entity_id in _TRACKED_ENTITY_IDS:
                _last_state[entity_id] = state
        return

    if msg_type != "state_changed":
        return

    entity_id = message.get("entity_id")
    if entity_id not in _TRACKED_ENTITY_IDS:
        return

    new_state = message.get("new_state")
    if new_state is None:
        _last_state.pop(entity_id, None)
        return

    old_state = _state_of(entity_id)
    _last_state[entity_id] = new_state

    try:
        _ENTITY_HANDLERS[entity_id](entity_id, old_state, new_state)
    except Exception:
        logger.exception("Falha ao processar automação pra %s", entity_id)


# ==========================================================
# 3+4. reset diário dos flags (06:00 / 00:00)
# ==========================================================

def _today() -> str:
    return datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d")


def _now_hm() -> str:
    now = datetime.now(timezone.utc).astimezone()
    return f"{now.hour:02d}:{now.minute:02d}"


async def _daily_reset_loop():
    while True:
        hm = _now_hm()
        today = _today()

        if hm == "06:00" and _daily_reset_last_date.get("bom_dia_executado_hoje") != today:
            _daily_flags["bom_dia_executado_hoje"] = False
            _daily_reset_last_date["bom_dia_executado_hoje"] = today

        if hm == "00:00" and _daily_reset_last_date.get("conversa_taiane_executada_hoje") != today:
            _daily_flags["conversa_taiane_executada_hoje"] = False
            _daily_reset_last_date["conversa_taiane_executada_hoje"] = today

        await asyncio.sleep(TICK_SECONDS)


def start_automations():
    ha_websocket_service.subscribe(_on_ws_message)
    asyncio.create_task(_daily_reset_loop())
