from datetime import datetime

class Runtime:

    def __init__(self):
        self.started=datetime.now()
        self.state="online"

    def uptime(self):
        return str(datetime.now()-self.started)

    def status(self):
        return {
            "state":self.state,
            "uptime":self.uptime()
        }

runtime=Runtime()
