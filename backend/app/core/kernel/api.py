from app.core.kernel.kernel import kernel


class KernelAPI:

    VERSION = "1.0.0"

    def info(self):
        return kernel.info()

    def registry(self):
        return kernel.registry().list()

    def services(self):
        return kernel.services().services()

    def service(self, name):
        return kernel.services().get(name)

    def plugins(self):
        return kernel.plugins().list()

    def events(self):
        return kernel.events().summary()

    def scheduler(self):
        return kernel.scheduler().stats()

    def discovery(self):
        return kernel.discovery()

    def health(self):

        return {
            "kernel": kernel.info(),
            "services": len(kernel.services().services()),
            "plugins": len(kernel.plugins().list()),
            "events": kernel.events().summary(),
            "scheduler": kernel.scheduler().stats(),
        }


api = KernelAPI()
