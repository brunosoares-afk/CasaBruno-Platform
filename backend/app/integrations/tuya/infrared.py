from .client import api

HUB_ID = "ebd5e5ed961cfe1111txzq"
TV_REMOTE = "eba153d0e197b62eeap9ia"
AC_REMOTE = "ebfd426b126b4752151ox3"
PROJECTOR_REMOTE = "ebad5da8824a00c518kage"

KEYS = {
    "power": "Power",
    "volume_up": "Volume+",
    "volume_down": "Volume-",
    "channel_up": "Channel+",
    "channel_down": "Channel-",
    "menu": "Menu",
    "up": "Up",
    "down": "Down",
    "left": "Left",
    "right": "Right",
    "ok": "confirm",
}


def send_ir(remote, key):
    return api.post(
        f"/v1.0/infrareds/{HUB_ID}/remotes/{remote}/command",
        {"key": KEYS[key]},
    )


# Teclas aprendidas manualmente no Projetor (id = key_id na Tuya)
PROJECTOR_KEYS = {
    "power": 1,
    "back": 116,
    "homepage": 136,
    "menu": 45,
    "mute": 106,
    "navigate_down": 47,
    "navigate_left": 48,
    "navigate_right": 49,
    "navigate_up": 46,
    "ok": 42,
    "volume_down": 51,
    "volume_up": 50,
}

PROJECTOR_CATEGORY_ID = 6


def send_ir_learned(remote, category_id, key, key_id):
    """Envia um codigo IR previamente aprendido (endpoint 'raw/command')."""
    return api.post(
        f"/v2.0/infrareds/{HUB_ID}/remotes/{remote}/raw/command",
        {
            "category_id": category_id,
            "key": key,
            "key_id": key_id,
        },
    )


# ==========================
# TV
# ==========================

def tv_power():
    return send_ir(TV_REMOTE, "power")

def tv_volume_up():
    return send_ir(TV_REMOTE, "volume_up")

def tv_volume_down():
    return send_ir(TV_REMOTE, "volume_down")

def tv_channel_up():
    return send_ir(TV_REMOTE, "channel_up")

def tv_channel_down():
    return send_ir(TV_REMOTE, "channel_down")

def tv_menu():
    return send_ir(TV_REMOTE, "menu")

def tv_up():
    return send_ir(TV_REMOTE, "up")

def tv_down():
    return send_ir(TV_REMOTE, "down")

def tv_left():
    return send_ir(TV_REMOTE, "left")

def tv_right():
    return send_ir(TV_REMOTE, "right")

def tv_ok():
    return send_ir(TV_REMOTE, "ok")


# ==========================
# PROJETOR (codigos aprendidos manualmente)
# ==========================

def _projector(key):
    return send_ir_learned(
        PROJECTOR_REMOTE,
        PROJECTOR_CATEGORY_ID,
        key,
        PROJECTOR_KEYS[key],
    )

def projector_power():
    return _projector("power")

def projector_up():
    return _projector("navigate_up")

def projector_down():
    return _projector("navigate_down")

def projector_left():
    return _projector("navigate_left")

def projector_right():
    return _projector("navigate_right")

def projector_ok():
    return _projector("ok")

def projector_home():
    return _projector("homepage")

def projector_back():
    return _projector("back")

def projector_menu():
    return _projector("menu")

def projector_mute():
    return _projector("mute")

def projector_volume_up():
    return _projector("volume_up")

def projector_volume_down():
    return _projector("volume_down")


# ==========================
# AR-CONDICIONADO (remote "Ar quarto", categoria "standard AC" na Tuya,
# marca TCL, category_id 5). Teclas aprendidas na nuvem: PowerOn, PowerOff,
# M (mode), F (fan), T (temperature) - confirmado via GET .../keys.
#
# GET /ac/status  -> funciona, devolve o ultimo estado conhecido
#                     (power/mode/temp/wind).
# POST/PUT /ac/status -> NAO funciona (API responde "uri path invalid"),
#                     apesar de alguns scripts antigos assumirem que sim.
#
# O envio real de comando e via /command com {"key": ...}, igual TV/projetor:
#   - PowerOn / PowerOff: confirmado funcionando (testado ao vivo).
#   - M / F / T (mode/fan/temp): a Tuya aceita a chave mas rejeita todo
#     payload de valor testado ("value", "key_id" etc) com
#     code 30706 "Command or value not supported". O formato certo do
#     valor pra essas 3 nao esta documentado aqui - precisa checar a
#     documentacao da Tuya IoT Platform pra essa categoria (ac/standard
#     remote) ou testar direto no simulador do painel Tuya.
# ==========================

def _ac_command_url():
    return f"/v1.0/infrareds/{HUB_ID}/remotes/{AC_REMOTE}/command"


def air_status():
    r = api.get(f"/v2.0/infrareds/{HUB_ID}/remotes/{AC_REMOTE}/ac/status")
    return r.get("result", r) if isinstance(r, dict) else r


def air_on():
    return api.post(_ac_command_url(), {"key": "PowerOn"})

def air_off():
    return api.post(_ac_command_url(), {"key": "PowerOff"})

def air_temp(temp):
    return api.post(_ac_command_url(), {"key": "T", "value": temp})

def air_mode(mode):
    return api.post(_ac_command_url(), {"key": "M", "value": mode})

def air_fan(speed):
    return api.post(_ac_command_url(), {"key": "F", "value": speed})
