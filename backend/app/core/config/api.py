from app.core.config.config import config


class ConfigAPI:

    def info(self):
        return config.summary()

    def all(self):
        return config.all()

    def get(self, section):
        return config.get(section)

    def set(self, section, data):
        config.set(section, data)
        return config.get(section)

    def reload(self):
        config.load()
        return config.summary()

    def save(self):
        config.save()
        return config.summary()


api = ConfigAPI()
