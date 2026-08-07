from app.core.events.bus import event_bus
from app.core.events.dispatcher import dispatcher


class EventManager:

    def emit(self, event, data=None):
        event_bus.publish(event, data)
        dispatcher.dispatch(event, data)

    def subscribe(self, event, callback):
        dispatcher.register(event, callback)

    def unsubscribe(self, event, callback):
        dispatcher.unregister(event, callback)

    def history(self):
        return event_bus.history

    def stats(self):
        return event_bus.stats()

    def listeners(self):
        return {
            event: len(callbacks)
            for event, callbacks in dispatcher.listeners.items()
        }

    def clear(self):
        event_bus.clear()

    def summary(self):
        return {
            "history": len(event_bus.history),
            "listeners": self.listeners(),
            "stats": self.stats(),
        }


event_manager = EventManager()
