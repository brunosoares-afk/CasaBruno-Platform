import subprocess


def adb(device, command):

    subprocess.run(
        ["adb", "-s", device] + command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )


def key(device, keycode):

    adb(device, [
        "shell",
        "input",
        "keyevent",
        str(keycode)
    ])


def home(device):
    key(device, 3)


def back(device):
    key(device, 4)


def menu(device):
    key(device, 82)


def up(device):
    key(device, 19)


def down(device):
    key(device, 20)


def left(device):
    key(device, 21)


def right(device):
    key(device, 22)


def ok(device):
    key(device, 23)


def power(device):
    key(device, 26)


def volume_up(device):
    key(device, 24)


def volume_down(device):
    key(device, 25)
