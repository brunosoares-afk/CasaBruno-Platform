import json
import os
from contextlib import asynccontextmanager
from pathlib import Path

import aiohttp
from aioamazondevices.api import AmazonEchoApi
from aioamazondevices.structures import AmazonMediaControls
from fastapi import FastAPI, HTTPException

LOGIN_DATA_PATH = Path("/data/login_data.json")
USERNAME = os.environ["ALEXA_USERNAME"]
PASSWORD = os.environ["ALEXA_PASSWORD"]

# entity_id que a HA já usava (alexa_devices) -> account_name real do
# aparelho, pra chamador continuar falando o mesmo entity_id de sempre.
DEVICE_BY_ENTITY = {
    "media_player.alexa_taiane": "Alexa Taiane",
    "media_player.bruno_s_n65b": "Bruno's N65B",
}

MEDIA_COMMANDS = {
    "play": AmazonMediaControls.Play,
    "pause": AmazonMediaControls.Pause,
    "stop": AmazonMediaControls.Stop,
    "next": AmazonMediaControls.Next,
    "previous": AmazonMediaControls.Previous,
}

state: dict = {"api": None, "session": None, "devices": {}}


async def _refresh_devices() -> None:
    await state["api"].login.login_mode_stored_data()
    state["devices"] = await state["api"].get_devices_data()


@asynccontextmanager
async def lifespan(app: FastAPI):
    login_data = json.loads(LOGIN_DATA_PATH.read_text())
    session = aiohttp.ClientSession()
    # save_to_file NÃO é "salvar sessão renovada" (achado tarde, corrompeu
    # o login_data.json uma vez — é um hook de debug que despeja QUALQUER
    # resposta HTTP da lib). Deliberadamente omitido. O access_token expira
    # mas o refresh_token deveria bastar pra login_mode_stored_data() renovar
    # sozinho a cada chamada, sem precisar persistir nada de volta — mesma
    # premissa que a própria HA usa (nunca reescreve login_data no config_entry
    # depois do setup inicial).
    api = AmazonEchoApi(session, USERNAME, PASSWORD, login_data)
    state["api"] = api
    state["session"] = session
    await _refresh_devices()
    yield
    await session.close()


app = FastAPI(lifespan=lifespan)


def _device_for_entity(entity_id: str):
    name = DEVICE_BY_ENTITY.get(entity_id)
    if not name:
        raise HTTPException(404, f"Dispositivo não mapeado: {entity_id}")
    for dev in state["devices"].values():
        if getattr(dev, "account_name", None) == name:
            return dev
    raise HTTPException(404, f"Dispositivo não encontrado na conta Amazon: {name}")


@app.get("/devices")
async def devices():
    return {
        serial: {"name": getattr(d, "account_name", None), "online": getattr(d, "online", None)}
        for serial, d in state["devices"].items()
    }


@app.post("/dnd")
async def dnd(entity_id: str, enable: bool):
    device = _device_for_entity(entity_id)
    await state["api"].set_do_not_disturb(device, enable)
    return {"success": True}


@app.post("/volume")
async def volume(entity_id: str, level: float):
    device = _device_for_entity(entity_id)
    # Alexa espera 0-100 (int), o resto do projeto usa 0.0-1.0 (padrão HA).
    await state["api"].set_device_volume(device, round(level * 100))
    return {"success": True}


@app.post("/media")
async def media(entity_id: str, command: str):
    device = _device_for_entity(entity_id)
    cmd = MEDIA_COMMANDS.get(command)
    if not cmd:
        raise HTTPException(400, f"Comando inválido: {command}")
    await state["api"].send_media_command(device, cmd)
    return {"success": True}


@app.post("/speak")
async def speak(entity_id: str, text: str):
    device = _device_for_entity(entity_id)
    await state["api"].call_alexa_speak(device, text)
    return {"success": True}


@app.get("/health")
async def health():
    return {"ok": True, "devices": len(state["devices"])}
