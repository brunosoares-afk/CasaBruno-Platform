from app.core.scheduler.scheduler import scheduler
from app.core.events.event_manager import event_manager


class SchedulerManager:

    def register(self, name, interval, callback, event=None):
        scheduler.register(
            name=name,
            interval=interval,
            callback=callback,
            event=event
        )

    def unregister(self, name):
        scheduler.unregister(name)

    def enable(self, name):
        scheduler.enable(name)

    def disable(self, name):
        scheduler.disable(name)

    def run(self):
        return scheduler.tick()

    def loop(self, delay=1):
        scheduler.loop(delay)

    def list(self):
        return scheduler.list()

    def stats(self):
        return {
            "jobs": len(scheduler.jobs),
            "executed": sum(
                job["runs"]
                for job in scheduler.jobs.values()
            ),
            "enabled": sum(
                1
                for job in scheduler.jobs.values()
                if job["enabled"]
            ),
            "events": event_manager.stats()
        }


scheduler_manager = SchedulerManager()
