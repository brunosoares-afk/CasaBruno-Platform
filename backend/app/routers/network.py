import re
import subprocess

from fastapi import APIRouter

from app.core.config.config import config

router = APIRouter(
    prefix="/network",
    tags=["Network"]
)


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


@router.get("/devices")
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
