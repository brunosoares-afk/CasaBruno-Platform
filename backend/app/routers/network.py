import asyncio
import re
import subprocess
import time
from collections import deque

from fastapi import APIRouter, Depends

from app.api.auth import require_gerencia_session
from app.core.config.config import config

router = APIRouter(
    prefix="/network",
    tags=["Network"]
)

PACKET_LOSS_TARGET = "8.8.8.8"
PACKET_LOSS_INTERVAL_S = 3
PACKET_LOSS_WINDOW = 100  # ~5 min de histórico com o intervalo acima

_packet_loss_samples = deque(maxlen=PACKET_LOSS_WINDOW)


async def _packet_loss_loop():
    while True:
        online, _ = await asyncio.to_thread(ping, PACKET_LOSS_TARGET)
        _packet_loss_samples.append((time.time(), online))
        await asyncio.sleep(PACKET_LOSS_INTERVAL_S)


def start_packet_loss_monitor():
    asyncio.create_task(_packet_loss_loop())


def ping(host, timeout=1):
    try:
        result = subprocess.run(
            ["ping", "-c", "1", "-W", str(timeout), host],
            capture_output=True,
            text=True,
            timeout=timeout + 1
        )
        online = result.returncode == 0
        latency = None
        if online:
            match = re.search(r"time=([\d.]+)", result.stdout)
            if match:
                latency = float(match.group(1))
        return online, latency
    except Exception:
        return False, None


def arp_online(host, timeout=1):
    try:
        result = subprocess.run(
            ["ip", "neigh", "show", host],
            capture_output=True,
            text=True,
            timeout=timeout + 1
        )
        return any(state in result.stdout for state in ("REACHABLE", "STALE", "DELAY"))
    except Exception:
        return False


@router.get("/devices", dependencies=[Depends(require_gerencia_session)])
def devices():
    cfg = config.get("network_devices", {}) or {}
    items = cfg.get("items", [])
    response = []
    for item in items:
        host = item.get("host")
        online, latency = ping(host)
        if not online:
            online = arp_online(host)
        response.append({
            "name": item.get("name"),
            "host": host,
            "online": online,
            "latency_ms": latency
        })
    return response


@router.get("/packet-loss")
def packet_loss():
    samples = list(_packet_loss_samples)
    total = len(samples)
    lost = sum(1 for _, online in samples if not online)
    loss_percent = round((lost / total) * 100, 1) if total else None
    return {
        "target": PACKET_LOSS_TARGET,
        "loss_percent": loss_percent,
        "window_size": total,
        "interval_s": PACKET_LOSS_INTERVAL_S,
    }
