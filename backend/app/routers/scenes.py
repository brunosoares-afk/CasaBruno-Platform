import subprocess
import threading
import time

from fastapi import APIRouter

from app.integrations.tuya import infrared as tuya_infrared

router = APIRouter(prefix="/scenes", tags=["Scenes"])

PROJECTOR_ADB_HOST = "192.168.20.248:5555"
BOOT_WAIT_SECONDS = 95  # ~1min20s de boot observado + folga de seguranca
APP_LOAD_WAIT_SECONDS = 5


def _adb(*args, timeout=10):
    try:
        return subprocess.run(
            ["/usr/local/bin/adb", *args],
            capture_output=True,
            text=True,
            timeout=timeout,
        ).stdout
    except subprocess.TimeoutExpired:
        return ""


def _key(keycode, timeout=10):
    _adb("-s", PROJECTOR_ADB_HOST, "shell", "input", "keyevent", keycode, timeout=timeout)


def _launch_app(package):
    _adb("-s", PROJECTOR_ADB_HOST, "shell", "monkey", "-p", package,
         "-c", "android.intent.category.LAUNCHER", "1")


def _run_scene_unitv():
    tuya_infrared.projector_power()
    time.sleep(BOOT_WAIT_SECONDS)
    _adb("connect", PROJECTOR_ADB_HOST)
    _launch_app("com.unitvnet.tvod")


def _run_scene_desenho_heitor():
    tuya_infrared.projector_power()
    time.sleep(BOOT_WAIT_SECONDS)
    _adb("connect", PROJECTOR_ADB_HOST)
    _launch_app("com.google.android.youtube.tv")
    time.sleep(APP_LOAD_WAIT_SECONDS)

    # Navega ate o campo de busca (sobe pra barra, um passo pra direita cai no campo de texto)
    _key("KEYCODE_DPAD_UP")
    time.sleep(1)
    _key("KEYCODE_DPAD_RIGHT")
    time.sleep(1)
    _key("KEYCODE_DPAD_CENTER")
    time.sleep(2)

    # Digita a busca (sem o "&", que o Android nao digita corretamente via ADB)
    _adb("-s", PROJECTOR_ADB_HOST, "shell", "input", "text", "NICK%sVLAD")
    time.sleep(1)

    # Navega ate o botao de confirmar busca no teclado virtual
    for _ in range(4):
        _key("KEYCODE_DPAD_DOWN")
        time.sleep(0.5)
    for _ in range(2):
        _key("KEYCODE_DPAD_RIGHT")
        time.sleep(0.5)
    _key("KEYCODE_ENTER")


@router.post("/unitv")
def scene_unitv():
    threading.Thread(target=_run_scene_unitv, daemon=True).start()
    return {
        "success": True,
        "message": f"Cena UNITV iniciada. Projetor ligando, app deve abrir em ~{BOOT_WAIT_SECONDS}s."
    }


@router.post("/desenho-heitor")
def scene_desenho_heitor():
    threading.Thread(target=_run_scene_desenho_heitor, daemon=True).start()
    return {
        "success": True,
        "message": f"Cena Desenho Heitor iniciada. Projetor ligando, busca deve completar em ~{BOOT_WAIT_SECONDS + 15}s."
    }
