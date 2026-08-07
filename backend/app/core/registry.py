class ServiceRegistry:

    def __init__(self):
        self._services = {}

    def register(self, name, service):
        self._services[name] = service

    def unregister(self, name):
        self._services.pop(name, None)

    def get(self, name):
        return self._services.get(name)

    def exists(self, name):
        return name in self._services

    def list(self):
        return list(self._services.keys())


registry = ServiceRegistry()
