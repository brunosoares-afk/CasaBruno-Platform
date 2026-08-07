import socket
import shutil
import psutil
import subprocess


def run(cmd):
    try:
        return subprocess.check_output(
            cmd,
            shell=True,
            text=True
        ).strip()
    except Exception:
        return "offline"


def get_system_status():

    total, used, free = shutil.disk_usage("/")

    return {

        "hostname": socket.gethostname(),

        "cpu_percent": psutil.cpu_percent(interval=0.5),

        "memory_percent": psutil.virtual_memory().percent,

        "disk_percent": round((used / total) * 100, 1),

        "uptime": run("uptime -p"),

        "docker": run("docker ps --format '{{.Names}}'").splitlines(),

        "internet": run("ping -c1 1.1.1.1 >/dev/null && echo online")

    }
