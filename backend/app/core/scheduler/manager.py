from app.core.scheduler.scheduler import scheduler


class SchedulerManager:

    def register(self, name, interval, callback, enabled=True):
        return scheduler.register(name, interval, callback, enabled)

    def unregister(self, name):
        return scheduler.unregister(name)

    def enable(self, name):
        return scheduler.enable(name)

    def disable(self, name):
        return scheduler.disable(name)

    def run(self, name):
        return scheduler.run(name)

    def tick(self):
        return scheduler.tick()

    def list(self):
        return scheduler.list()

    def clear(self):
        return scheduler.clear()

    def stats(self):
        return {
            "jobs": len(scheduler.jobs),
            "registered": list(scheduler.jobs.keys()),
            "details": scheduler.list(),
        }


scheduler_manager = SchedulerManager()
