import docker
from datetime import datetime

client = docker.from_env()


def get_containers():

    containers = []

    for c in client.containers.list(all=True):

        c.reload()

        ports = []

        if c.attrs["NetworkSettings"]["Ports"]:
            for porta, host in c.attrs["NetworkSettings"]["Ports"].items():
                if host:
                    ports.append(
                        f"{host[0]['HostPort']} → {porta}"
                    )

        redes = list(
            c.attrs["NetworkSettings"]["Networks"].keys()
        )

        ip = ""

        if redes:
            ip = c.attrs["NetworkSettings"]["Networks"][redes[0]].get(
                "IPAddress", ""
            )

        containers.append({

            "id": c.short_id,

            "name": c.name,

            "image": c.image.tags[0] if c.image.tags else "sem tag",

            "status": c.status,

            "created": c.attrs["Created"],

            "ports": ports,

            "networks": redes,

            "ip": ip

        })

    return containers
