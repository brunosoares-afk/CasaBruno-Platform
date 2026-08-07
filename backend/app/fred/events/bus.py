class EventBus:

    def __init__(self):
        self.events=[]

    def emit(self,name,payload=None):
        self.events.append({
            "event":name,
            "payload":payload
        })

    def history(self):
        return self.events

bus=EventBus()
