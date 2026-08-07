from datetime import datetime


class Scheduler:

    def __init__(self):
        self.jobs = {}

    def register(self, name, interval, callback, enabled=True):
        self.jobs[name] = {
            "name": name,
            "interval": interval,
            "callback": callback,
            "enabled": enabled,
            "last_run": None,
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

        job["callback"]()
        job["runs"] += 1
        job["last_run"] = datetime.now().isoformat()

        return True

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
