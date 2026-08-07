class Discovery:

    def __init__(self):
        self.items = {}

    def scan(self):
        return self.items

    # Compatibilidade com versões anteriores
    def discover(self):
        return self.scan()

    def list(self):
        return list(self.items.keys())

    def register(self, name, obj):
        self.items[name] = obj
        return True

    def unregister(self, name):
        if name in self.items:
            del self.items[name]
            return True
        return False

    def get(self, name):
        return self.items.get(name)

    def exists(self, name):
        return name in self.items

    def clear(self):
        self.items.clear()

    def stats(self):
        return {
            "count": len(self.items),
            "items": self.list()
        }

    def summary(self):
        return {
            "count": len(self.items),
            "items": self.list()
        }


discovery = Discovery()
