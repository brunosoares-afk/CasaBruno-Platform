import time
from datetime import datetime

from app.core.events.event_manager import event_manager


class Scheduler:

    def __init__(self):
        self.jobs = {}

    def register(self, name, interval, callback, enabled=True, event=None):
        self.jobs[name] = {
            "name": name,
            "interval": interval,
            "callback": callback,
            "enabled": enabled,
            "event": event,
            "last_run": None,
            "last_tick": None,
            "runs": 0
        }

    def unregister(self, name):
        if name in self.jobs:
            del self.jobs[name]
            return True
        return False

    def clear(self):
        self.jobs.clear()
        return True

    def exists(self, name):
        return name in self.jobs

    def get(self, name):
        return self.jobs.get(name)

    def enable(self, name):
        if name in self.jobs:
            self.jobs[name]["enabled"] = True
            return True
        return False

    def disable(self, name):
        if name in self.jobs:
            self.jobs[name]["enabled"] = False
            return True
        return False

    def run(self, name):
        job = self.jobs.get(name)

        if job is None:
            return False

        if not job["enabled"]:
            return False

        result = job["callback"]()
        job["runs"] += 1
        job["last_run"] = datetime.now().isoformat()

        if job["event"]:
            event_manager.emit(job["event"], result)

        return True

    def tick(self):
        now = time.time()
        executed = []

        for name, job in self.jobs.items():

            if not job["enabled"]:
                continue

            due = (
                job["last_tick"] is None
                or (now - job["last_tick"]) >= job["interval"]
            )

            if not due:
                continue

            job["last_tick"] = now
            self.run(name)
            executed.append(name)

        return executed

    def loop(self, delay=1):
        while True:
            self.tick()
            time.sleep(delay)

    def list(self):
        return list(self.jobs.keys())

    def details(self):
        return self.jobs

    def stats(self):
        return {
            "jobs": len(self.jobs),
            "registered": self.list(),
            "details": self.details()
        }


scheduler = Scheduler()
