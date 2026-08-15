import asyncio
import logging
from datetime import datetime, timedelta, timezone

from app.integrations.google import calendar as google_calendar
from app.services import memory_service, notify_service, weather_service
from app.services.homeassistant_service import get_states
from app.services.fred_memory import memory as fred_memory

# Fase 8 — quem recebe os avisos proativos hoje (settings.FRED_NOTIFY_JID
# aponta pro JID do Bruno), pra saber de quem é a "confirmação pendente"
# quando ele responde "sim"/"pode" no WhatsApp.
NOTIFY_PERSON = "Bruno"

logger = logging.getLogger("scheduler_service")
logger.setLevel(logging.INFO)
if not logging.getLogger().handlers:
    logging.basicConfig(level=logging.INFO)

TICK_SECONDS = 60
WEATHER_HOUR = 8
AGENDA_HOUR = 21

# "Já rodou hoje" por job — em memória, cai num restart (mesma
# limitação já aceita pras sessões da Gerência em auth.py). Chaves:
# nome do job -> data (YYYY-MM-DD) da última execução.
_last_run: dict[str, str] = {}

# A mensagem de "agenda não conectada" só deve ser mandada uma vez na
# vida, não repetir todo dia — controlada à parte do _last_run diário.
_agenda_not_connected_notified = False


def _today() -> str:
    return datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d")


def _now_hour() -> int:
    return datetime.now(timezone.utc).astimezone().hour


async def _weather_job():
    if _last_run.get("weather") == _today() or _now_hour() < WEATHER_HOUR:
        return
    _last_run["weather"] = _today()

    try:
        weather = await asyncio.to_thread(weather_service.get_current)
        temp = weather["temperature"]

        message = f"Bom dia! Hoje o tempo está {weather['label']}"
        message += f", {round(temp)}°C." if temp is not None else "."
        await notify_service.notify(message)
    except Exception:
        logger.exception("Falha no job de previsão do tempo")


async def _agenda_job():
    global _agenda_not_connected_notified

    if _last_run.get("agenda") == _today() or _now_hour() < AGENDA_HOUR:
        return
    _last_run["agenda"] = _today()

    try:
        if not google_calendar.is_connected():
            if not _agenda_not_connected_notified:
                _agenda_not_connected_notified = True
                await notify_service.notify(
                    "Ainda não tenho sua Agenda do Google conectada, então não "
                    "consigo avisar sobre amanhã — configure em Gerência quando puder."
                )
            return

        tomorrow = (datetime.now(timezone.utc).astimezone() + timedelta(days=1)).strftime("%Y-%m-%d")
        events = google_calendar.list_upcoming_events(max_results=20)
        tomorrow_events = [
            e for e in events
            if (e.get("start", {}).get("dateTime") or e.get("start", {}).get("date") or "").startswith(tomorrow)
        ]

        if not tomorrow_events:
            await notify_service.notify("Nenhum compromisso na agenda pra amanhã.")
            return

        titles = "; ".join(e.get("summary", "(sem título)") for e in tomorrow_events)
        await notify_service.notify(f"Pra amanhã na agenda: {titles}.")
    except Exception:
        logger.exception("Falha no job de agenda")


async def _lamp_job():
    if _last_run.get("lamp") == _today():
        return

    try:
        states = get_states()
        sun = next((s for s in states if s.get("entity_id") == "sun.sun"), None)
        if not sun or sun.get("state") != "above_horizon":
            return

        lights_on = [
            s for s in states
            if s.get("entity_id", "").startswith("light.") and s.get("state") == "on"
        ]
        if not lights_on:
            return

        _last_run["lamp"] = _today()
        names = ", ".join(
            s.get("attributes", {}).get("friendly_name", s["entity_id"]) for s in lights_on
        )
        sent = await notify_service.notify(f"A luz {names} ficou ligada de dia, quer que eu apague?")

        # Fase 8 — guarda o que "sim" deve fazer se ele responder, senão
        # a pergunta é só decorativa (a resposta nunca desligava nada de
        # verdade antes disso). Só grava se o aviso saiu, senão uma
        # resposta "sim" sem pergunta de verdade na tela confundiria.
        if sent:
            fred_memory.remember(
                NOTIFY_PERSON,
                "pending_confirmation",
                {"action": "turn_off", "entity_ids": [s["entity_id"] for s in lights_on]},
            )
    except Exception:
        logger.exception("Falha no job de lâmpada ligada durante o dia")


async def _reminders_job():
    try:
        due = memory_service.get_due_reminders(_today())
        for reminder in due:
            text = f"Lembrete: {reminder['name']}."
            if reminder.get("description"):
                text += f" {reminder['description']}"
            sent = await notify_service.notify(text)
            if sent:
                memory_service.mark_reminder_notified(reminder["id"])
    except Exception:
        logger.exception("Falha no job de lembretes")


async def _scheduler_loop():
    while True:
        await _weather_job()
        await _agenda_job()
        await _lamp_job()
        await _reminders_job()
        await asyncio.sleep(TICK_SECONDS)


def start_scheduler():
    asyncio.create_task(_scheduler_loop())
