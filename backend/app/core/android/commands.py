import subprocess

ADB_BIN = "/usr/local/bin/adb"


def adb(device, command):

    return subprocess.run(
        [ADB_BIN, "-s", device] + command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )


def key(device, keycode):

    return adb(device, [
        "shell",
        "input",
        "keyevent",
        str(keycode)
    ])


def home(device):
    return key(device, 3)


def back(device):
    return key(device, 4)


def menu(device):
    return key(device, 82)


def up(device):
    return key(device, 19)


def down(device):
    return key(device, 20)


def left(device):
    return key(device, 21)


def right(device):
    return key(device, 22)


def ok(device):
    return key(device, 23)


def power(device):
    return key(device, 26)


def volume_up(device):
    return key(device, 24)


def volume_down(device):
    return key(device, 25)
