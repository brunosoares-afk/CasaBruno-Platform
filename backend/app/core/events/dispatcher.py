from collections import defaultdict


class EventDispatcher:

    def __init__(self):
        self.listeners = defaultdict(list)

    def register(self, event, callback):

        if callback not in self.listeners[event]:
            self.listeners[event].append(callback)

    def unregister(self, event, callback):

        if callback in self.listeners[event]:
            self.listeners[event].remove(callback)

    def dispatch(self, event, data=None):

        executed = 0

        for callback in self.listeners.get(event, []):

            try:
                callback(data)
                executed += 1
            except Exception:
                pass

        return executed

    def events(self):
        return list(self.listeners.keys())

    def listeners_count(self):

        return {
            event: len(callbacks)
            for event, callbacks in self.listeners.items()
        }


dispatcher = EventDispatcher()
