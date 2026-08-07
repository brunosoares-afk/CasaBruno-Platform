from app.core.kernel.kernel import kernel
from app.core.events.event_manager import event_manager
from app.core.scheduler.manager import scheduler_manager
from app.core.plugin_loader import plugin_loader


class Application:

    NAME = "CasaBruno Platform"
    VERSION = "2.0.0"

    def __init__(self):
        self.running = False

    def start(self):

        if self.running:
            return False

        plugin_loader.load()

        event_manager.emit(
            "application.start",
            {
                "application": self.NAME,
                "version": self.VERSION
            }
        )

        self.running = True
        return True

    def stop(self):

        if not self.running:
            return False

        event_manager.emit(
            "application.stop",
            {
                "application": self.NAME,
                "version": self.VERSION
            }
        )

        scheduler_manager.clear()

        self.running = False
        return True

    def restart(self):
        self.stop()
        self.start()
        return True

    def status(self):
        return {
            "application": self.NAME,
            "version": self.VERSION,
            "running": self.running
        }

    def kernel(self):
        return kernel


application = Application()
