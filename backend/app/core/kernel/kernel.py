from app.core.discovery import discovery
from app.core.registry2 import registry2
from app.core.service_manager2 import service_manager2
from app.core.plugin_manager import plugin_manager
from app.core.plugin_loader import plugin_loader
from app.core.events.event_manager import event_manager
from app.core.scheduler.manager import scheduler_manager


class Kernel:

    NAME = "CasaBruno Kernel"
    VERSION = "2.0.0"

    def info(self):
        return {
            "name": self.NAME,
            "version": self.VERSION,
        }

    def discovery(self):
        return discovery

    def registry(self):
        return registry2

    def services(self):
        return service_manager2

    def plugins(self):
        return plugin_manager

    def events(self):
        return event_manager

    def scheduler(self):
        return scheduler_manager

    def health(self):
        return {
            "kernel": self.info(),
            "services": len(self.registry().list()),
            "plugins": len(self.plugins().list()),
            "events": self.events().summary(),
            "scheduler": self.scheduler().stats(),
        }

    # Compatibilidade
    def summary(self):
        return self.health()


kernel = Kernel()
