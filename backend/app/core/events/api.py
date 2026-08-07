from app.core.events.event import Event


class EventsAPI:

    VERSION = "2.0.0"

    def __init__(self):
        self.events = []

    def summary(self):
        return {
            "version": self.VERSION,
            "events": len(self.events)
        }

    def emit(self, name, payload=None):
        event = Event(name, payload)
        self.events.append(event)
        return event.status()

    def all(self):
        return [
            event.status()
            for event in self.events
        ]

    def count(self):
        return len(self.events)

    def last(self):
        if not self.events:
            return None

        return self.events[-1].status()

    def process_last(self):
        if not self.events:
            return None

        return self.events[-1].process()

    def clear(self):
        self.events.clear()
        return {
            "success": True
        }


api = EventsAPI()
