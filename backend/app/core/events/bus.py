from datetime import datetime


class EventBus:

    def __init__(self):
        self.subscribers = {}
        self.history = []

    def subscribe(self, event, callback):

        if event not in self.subscribers:
            self.subscribers[event] = []

        if callback not in self.subscribers[event]:
            self.subscribers[event].append(callback)

    def unsubscribe(self, event, callback):

        if event in self.subscribers:

            if callback in self.subscribers[event]:
                self.subscribers[event].remove(callback)

    def publish(self, event, data=None):

        self.history.append({
            "event": event,
            "data": data,
            "time": datetime.now().isoformat()
        })

        for callback in self.subscribers.get(event, []):

            try:
                callback(data)
            except Exception:
                pass

    def subscribers_list(self):
        return {
            event: len(callbacks)
            for event, callbacks in self.subscribers.items()
        }

    def events(self):
        return list(self.subscribers.keys())

    def stats(self):

        stats = {}

        for item in self.history:
            name = item["event"]
            stats[name] = stats.get(name, 0) + 1

        return stats

    def clear(self):
        self.history.clear()


event_bus = EventBus()
