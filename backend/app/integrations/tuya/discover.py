from .client import status
from .client import functions
from .client import specifications
from .devices import TV
from .devices import AIR
from .devices import PROJECTOR
from .devices import SMART_IR

DEVICES = {
    "tv": TV,
    "air": AIR,
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
