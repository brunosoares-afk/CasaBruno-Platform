import datetime

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

from app.core.config.config import config

SCOPES = ["https://www.googleapis.com/auth/calendar"]

DEFAULT_CREDENTIALS_CONFIG = {
    "client_id": "",
    "client_secret": "",
    "redirect_uri": "",
}


def get_credentials_config():
    return {**DEFAULT_CREDENTIALS_CONFIG, **(config.get("google_calendar") or {})}


def is_configured():
    creds = get_credentials_config()
    return bool(creds["client_id"] and creds["client_secret"] and creds["redirect_uri"])


def _client_config():
    creds = get_credentials_config()
    return {
        "web": {
            "client_id": creds["client_id"],
            "client_secret": creds["client_secret"],
            "redirect_uris": [creds["redirect_uri"]],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
        }
    }


def _new_flow():
    # PKCE desligado de propósito: build_auth_url() e exchange_code() criam
    # cada um seu próprio Flow (chamadas HTTP separadas, sem estado
    # compartilhado), então o code_verifier gerado automaticamente na
    # primeira nunca chegaria na segunda — "Missing code verifier" do
    # Google. Não é necessário aqui mesmo: PKCE existe pra proteger
    # clientes públicos que não guardam client_secret, e este é um fluxo
    # "web" server-to-server com client_secret já configurado.
    creds = get_credentials_config()
    return Flow.from_client_config(
        _client_config(),
        scopes=SCOPES,
        redirect_uri=creds["redirect_uri"],
        autogenerate_code_verifier=False,
    )


def build_auth_url():
    flow = _new_flow()
    auth_url, _ = flow.authorization_url(access_type="offline", prompt="consent", include_granted_scopes="true")
    return auth_url


def exchange_code(code):
    flow = _new_flow()
    flow.fetch_token(code=code)
    _save_token(flow.credentials)


def _save_token(credentials):
    config.set("google_calendar_token", {
        "token": credentials.token,
        "refresh_token": credentials.refresh_token,
        "token_uri": credentials.token_uri,
        "client_id": credentials.client_id,
        "client_secret": credentials.client_secret,
        "scopes": credentials.scopes,
        "expiry": credentials.expiry.isoformat() if credentials.expiry else None,
    })


def is_connected():
    token = config.get("google_calendar_token")
    return bool(token and token.get("refresh_token"))


def _load_credentials():
    token = config.get("google_calendar_token")
    if not token:
        return None

    credentials = Credentials(
        token=token.get("token"),
        refresh_token=token.get("refresh_token"),
        token_uri=token.get("token_uri"),
        client_id=token.get("client_id"),
        client_secret=token.get("client_secret"),
        scopes=token.get("scopes"),
    )

    if credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())
        _save_token(credentials)

    return credentials


def list_upcoming_events(max_results=10):
    credentials = _load_credentials()
    if not credentials:
        return []

    service = build("calendar", "v3", credentials=credentials)
    now = datetime.datetime.utcnow().isoformat() + "Z"

    result = service.events().list(
        calendarId="primary",
        timeMin=now,
        maxResults=max_results,
        singleEvents=True,
        orderBy="startTime",
    ).execute()

    return result.get("items", [])


def create_event(summary, start_iso, end_iso, description=None):
    credentials = _load_credentials()
    if not credentials:
        raise RuntimeError("Google Agenda não conectada")

    service = build("calendar", "v3", credentials=credentials)

    event = {
        "summary": summary,
        "description": description,
        "start": {"dateTime": start_iso},
        "end": {"dateTime": end_iso},
    }

    return service.events().insert(calendarId="primary", body=event).execute()
