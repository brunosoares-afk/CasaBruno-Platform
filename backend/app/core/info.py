import platform
import socket
import os

from config.settings import settings


def get_system_info():

    return {

        "project": settings.PROJECT_NAME,

        "version": settings.VERSION,

        "hostname": socket.gethostname(),

        "system": platform.system(),

        "release": platform.release(),

        "machine": platform.machine(),

        "python": platform.python_version(),

        "pid": os.getpid()

    }
