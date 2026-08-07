from fastapi import APIRouter

from app.integrations.tuya import tv
from app.integrations.tuya import discover
from app.integrations.tuya import infrared

router = APIRouter(
    prefix="/tuya",
    tags=["Tuya"]
)

# ==========================
# TUYA NATIVO
# ==========================

@router.post("/tv/on")
def tv_on():
    return tv.power(True)

@router.post("/tv/off")
def tv_off():
    return tv.power(False)

@router.post("/tv/volume/up")
def tv_volume_up():
    return tv.volume(1)

@router.post("/tv/volume/down")
def tv_volume_down():
    return tv.volume(-1)

@router.post("/tv/channel/up")
def tv_channel_up():
    return tv.channel(1)

@router.post("/tv/channel/down")
def tv_channel_down():
    return tv.channel(-1)

# "air" nao e um device Tuya nativo (e um remote de IR) - as rotas abaixo
# usam a mesma implementacao de /ir/air/*, via infrared.air_* (.../ac/status).

@router.post("/air/on")
def air_on():
    return infrared.air_on()

@router.post("/air/off")
def air_off():
    return infrared.air_off()

@router.post("/air/temp/{temp}")
def air_temp(temp: int):
    return infrared.air_temp(temp)

@router.post("/air/mode/{mode}")
def air_mode(mode: str):
    return infrared.air_mode(mode)

@router.post("/air/fan/{speed}")
def air_fan(speed: str):
    return infrared.air_fan(speed)

@router.get("/air/status")
def air_status():
    return infrared.air_status()

# ==========================
# SMART IR - TV
# ==========================

@router.post("/ir/tv/power")
def ir_tv_power():
    return infrared.tv_power()

@router.post("/ir/tv/volume/up")
def ir_tv_volume_up():
    return infrared.tv_volume_up()

@router.post("/ir/tv/volume/down")
def ir_tv_volume_down():
    return infrared.tv_volume_down()

@router.post("/ir/tv/channel/up")
def ir_tv_channel_up():
    return infrared.tv_channel_up()

@router.post("/ir/tv/channel/down")
def ir_tv_channel_down():
    return infrared.tv_channel_down()

@router.post("/ir/tv/up")
def ir_tv_up():
    return infrared.tv_up()

@router.post("/ir/tv/down")
def ir_tv_down():
    return infrared.tv_down()

@router.post("/ir/tv/left")
def ir_tv_left():
    return infrared.tv_left()

@router.post("/ir/tv/right")
def ir_tv_right():
    return infrared.tv_right()

@router.post("/ir/tv/ok")
def ir_tv_ok():
    return infrared.tv_ok()

@router.post("/ir/tv/menu")
def ir_tv_menu():
    return infrared.tv_menu()

# ==========================
# SMART IR - PROJETOR
# ==========================

@router.post("/ir/projector/power")
def ir_projector_power():
    return infrared.projector_power()

@router.post("/ir/projector/up")
def ir_projector_up():
    return infrared.projector_up()

@router.post("/ir/projector/down")
def ir_projector_down():
    return infrared.projector_down()

@router.post("/ir/projector/left")
def ir_projector_left():
    return infrared.projector_left()

@router.post("/ir/projector/right")
def ir_projector_right():
    return infrared.projector_right()

@router.post("/ir/projector/ok")
def ir_projector_ok():
    return infrared.projector_ok()

@router.post("/ir/projector/home")
def ir_projector_home():
    return infrared.projector_home()

@router.post("/ir/projector/back")
def ir_projector_back():
    return infrared.projector_back()

@router.post("/ir/projector/menu")
def ir_projector_menu():
    return infrared.projector_menu()

@router.post("/ir/projector/mute")
def ir_projector_mute():
    return infrared.projector_mute()

@router.post("/ir/projector/volume/up")
def ir_projector_volume_up():
    return infrared.projector_volume_up()

@router.post("/ir/projector/volume/down")
def ir_projector_volume_down():
    return infrared.projector_volume_down()

# ==========================
# SMART IR - AR
# ==========================

@router.post("/ir/air/on")
def ir_air_on():
    return infrared.air_on()

@router.post("/ir/air/off")
def ir_air_off():
    return infrared.air_off()

@router.post("/ir/air/temp/{temp}")
def ir_air_temp(temp: int):
    return infrared.air_temp(temp)

@router.post("/ir/air/mode/{mode}")
def ir_air_mode(mode: int):
    return infrared.air_mode(mode)

@router.post("/ir/air/fan/{speed}")
def ir_air_fan(speed: int):
    return infrared.air_fan(speed)

# ==========================
# DISCOVERY
# ==========================

@router.get("/devices")
def devices():
    return discover.all()

@router.get("/functions")
def functions():
    return discover.funcs()

@router.get("/specifications")
def specifications():
    return discover.specs()
