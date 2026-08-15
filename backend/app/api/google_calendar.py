from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel

from app.integrations.google import calendar as google_calendar

router = APIRouter(
    prefix="/google/calendar",
    tags=["Google Calendar"]
)


class EventCreate(BaseModel):

    summary: str
    start: str
    end: str
    description: str | None = None


@router.get("/status")
def status():
    return {
        "configured": google_calendar.is_configured(),
        "connected": google_calendar.is_connected(),
    }


@router.get("/auth-url")
def auth_url():
    if not google_calendar.is_configured():
        raise HTTPException(status_code=400, detail="Credenciais do Google não configuradas (Gerência → Configurações)")
    return {"url": google_calendar.build_auth_url()}


@router.get("/callback")
def callback(code: str):
    if not google_calendar.is_configured():
        raise HTTPException(status_code=400, detail="Credenciais do Google não configuradas")
    google_calendar.exchange_code(code)
    return RedirectResponse(url="/casa/?page=homeassistant")


@router.get("/events")
def events(max_results: int = 10):
    if not google_calendar.is_connected():
        return []
    return google_calendar.list_upcoming_events(max_results=max_results)


@router.post("/events")
def create_event(data: EventCreate):
    if not google_calendar.is_connected():
        raise HTTPException(status_code=400, detail="Google Agenda não conectada")
    return google_calendar.create_event(data.summary, data.start, data.end, data.description)
