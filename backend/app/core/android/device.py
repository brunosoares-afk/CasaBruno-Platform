class AndroidDevice:

    def __init__(self, id, name, host):

        self.id = id
        self.name = name
        self.host = host

    def json(self):

        return {

            "id": self.id,
            "name": self.name,
            "host": self.host

        }
