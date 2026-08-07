from app.core.host import host


class HostService:

    def info(self):

        return {

            "hostname": host.hostname(),

            "ip": host.ip(),

            "cpu": {

                "load": host.cpu()

            },

            "memory": host.memory(),

            "disk": host.disk()

        }


host_service = HostService()
