from app.core.storage.storage import storage


class StorageAPI:

    def info(self):
        return storage.summary()

    def list(self):
        return storage.list()

    def read(self, name):
        return storage.read(name)

    def write(self, name, data):
        storage.write(name, data)
        return storage.read(name)

    def delete(self, name):
        return {
            "success": storage.delete(name)
        }

    def exists(self, name):
        return {
            "exists": storage.exists(name)
        }


api = StorageAPI()
