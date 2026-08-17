import asyncio
import logging

from app.config.settings import settings
from app.integrations.dvrip.asyncio_dvrip import DVRIPCam, SomethingIsWrongWithCamera

logger = logging.getLogger("ptz_service")
logger.setLevel(logging.INFO)
if not logging.getLogger().handlers:
    logging.basicConfig(level=logging.INFO)

# Mesma ideia do tuya_service.ENTITY_TO_DEVICE: entity_id do HA -> chave do
# dispositivo. Credenciais vêm do .env (settings), não de config.json — só
# a câmera da frente tem PTZ hoje (a de trás/Yoosee é fixa, ver
# [[casa-bruno-camera-fundo-hevc]]).
ENTITY_TO_DEVICE = {
    "camera.camera_icsee_frente": "camera_icsee_frente",
}

_DEVICES = {
    "camera_icsee_frente": {
        "host": settings.DVRIP_CAMERA_ICSEE_FRENTE_HOST,
        "user": settings.DVRIP_CAMERA_ICSEE_FRENTE_USER,
        "password": settings.DVRIP_CAMERA_ICSEE_FRENTE_PASSWORD,
    },
}

MANAGED_ENTITY_IDS = set(ENTITY_TO_DEVICE.keys())

VALID_COMMANDS = {
    "Stop", "DirectionUp", "DirectionDown", "DirectionLeft", "DirectionRight",
    "DirectionLeftUp", "DirectionLeftDown", "DirectionRightUp", "DirectionRightDown",
    "ZoomTile", "ZoomWide", "FocusNear", "FocusFar", "IrisSmall", "IrisLarge",
    "SetPreset", "GotoPreset", "ClearPreset", "StartTour", "StopTour",
}


def is_managed(entity_id: str) -> bool:
    return entity_id in ENTITY_TO_DEVICE


def device_key_for(entity_id: str) -> str | None:
    return ENTITY_TO_DEVICE.get(entity_id)


async def _move_async(device_key: str, cmd: str, step: int = 5, preset: int = -1) -> bool:
    cfg = _DEVICES[device_key]
    cam = DVRIPCam(cfg["host"], user=cfg["user"], password=cfg["password"])
    try:
        loop = asyncio.get_running_loop()
        ok = await cam.login(loop)
        if not ok:
            logger.error("Falha de login DVR-IP na câmera %s", device_key)
            return False
        await cam.ptz(cmd, step=step, preset=preset)
        return True
    except SomethingIsWrongWithCamera:
        logger.exception("Câmera %s inacessível (DVR-IP)", device_key)
        return False
    finally:
        cam.close()


def move(device_key: str, cmd: str, step: int = 5, preset: int = -1) -> bool:
    if cmd not in VALID_COMMANDS:
        logger.error("Comando PTZ inválido: %s", cmd)
        return False
    try:
        return asyncio.run(_move_async(device_key, cmd, step=step, preset=preset))
    except Exception:
        logger.exception("Falha ao mover PTZ: %s", device_key)
        return False
