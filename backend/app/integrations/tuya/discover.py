from .client import status
from .client import functions
from .client import specifications
from .devices import TV
from .devices import PROJECTOR
from .devices import SMART_IR

# "air" (o remote de IR do ar-condicionado) nao entra aqui: nao e um device
# Tuya nativo, e sim um remote dentro do hub de infravermelho (SMART_IR),
# controlado via infrared.air_* / GET-POST em .../ac/status.
DEVICES = {
    "tv": TV,
    "projector": PROJECTOR,
    "smart_ir": SMART_IR
}

def all():
    data = {}
    for name, device in DEVICES.items():
        data[name] = status(device)
    return data

def funcs():
    data = {}
    for name, device in DEVICES.items():
        data[name] = functions(device)
    return data

def specs():
    data = {}
    for name, device in DEVICES.items():
        data[name] = specifications(device)
    return data
