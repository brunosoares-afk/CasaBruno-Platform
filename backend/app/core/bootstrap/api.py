from app.core.bootstrap.bootstrap import bootstrap


class BootstrapAPI:

    def info(self):
        return bootstrap.status()

    def start(self):
        bootstrap.start()
        return bootstrap.status()

    def stop(self):
        bootstrap.stop()
        return bootstrap.status()

    def restart(self):
        bootstrap.restart()
        return bootstrap.status()

    def discovery(self):
        return bootstrap.discovery()

    def services(self):
        return bootstrap.services()

    def plugins(self):
        return bootstrap.plugins()


api = BootstrapAPI()
