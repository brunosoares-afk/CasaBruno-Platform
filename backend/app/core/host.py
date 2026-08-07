import os
import shutil
import socket
import subprocess


class HostInfo:

    def hostname(self):

        return socket.gethostname()

    def ip(self):

        try:

            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

            s.connect(("8.8.8.8", 80))

            ip = s.getsockname()[0]

            s.close()

            return ip

        except Exception:

            return "0.0.0.0"

    def disk(self):

        total, used, free = shutil.disk_usage("/")

        return {

            "total": total,

            "used": used,

            "free": free

        }

    def memory(self):

        try:

            meminfo = {}

            with open("/proc/meminfo") as f:

                for line in f:

                    key, value = line.split(":", 1)

                    meminfo[key] = int(
                        value.strip().split()[0]
                    ) * 1024

            total = meminfo.get(
                "MemTotal",
                0
            )

            free = (
                meminfo.get("MemFree", 0)
                + meminfo.get("Buffers", 0)
                + meminfo.get("Cached", 0)
            )

            used = total - free

            return {

                "total": total,

                "used": used,

                "free": free

            }

        except Exception as e:

            return {

                "error": str(e)

            }

    def cpu(self):

        try:

            return os.getloadavg()

        except Exception:

            return (0, 0, 0)


host = HostInfo()
