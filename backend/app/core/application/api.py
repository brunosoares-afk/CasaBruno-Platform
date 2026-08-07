from app.core.application.application import application


class ApplicationAPI:

    def info(self):
        return application.status()

    def start(self):
        application.start()
        return application.status()

    def stop(self):
        application.stop()
        return application.status()

    def restart(self):
        application.restart()
        return application.status()

    def kernel(self):
        return application.kernel().summary()


api = ApplicationAPI()
