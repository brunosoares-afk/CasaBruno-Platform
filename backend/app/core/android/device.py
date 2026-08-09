class AndroidDevice:

    def __init__(self, id, name, host, mac=None):

        self.id = id
        self.name = name
        self.host = host
        self.mac = mac

    def json(self):

        return {

            "id": self.id,
            "name": self.name,
            "host": self.host,
            "mac": self.mac

        }
