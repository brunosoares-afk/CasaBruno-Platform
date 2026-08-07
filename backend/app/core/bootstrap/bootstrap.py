from app.core.discovery import discovery
from app.core.registry2 import registry2
from app.core.service_manager2 import service_manager2
from app.core.plugin_loader import plugin_loader
from app.core.plugin_manager import plugin_manager
from app.core.events.event_manager import event_manager
from app.core.scheduler.manager import scheduler_manager


class Bootstrap:

    VERSION = "2.0.0"

    def __init__(self):
        self.started = False

    def start(self):

        if self.started:
            return False

        discovery.scan()
        plugin_loader.load()

        event_manager.emit(
            "bootstrap.start",
            {
                "version": self.VERSION
            }
        )

        self.started = True
        return True

    def stop(self):

        if not self.started:
            return False

        scheduler_manager.clear()

        event_manager.emit(
            "bootstrap.stop",
            {
                "version": self.VERSION
            }
        )

        self.started = False
        return True

    def restart(self):
        self.stop()
        self.start()
        return True

    def discovery(self):
        return discovery.summary()

    def services(self):
        return service_manager2.services()

    def plugins(self):
        return plugin_manager.list()

    def status(self):
        return {
            "started": self.started,
            "version": self.VERSION,
            "services": len(self.services()),
            "plugins": len(self.plugins())
        }


bootstrap = Bootstrap()
