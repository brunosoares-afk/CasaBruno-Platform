import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from app.core.scheduler.scheduler import scheduler
from app.core.events.event_manager import event_manager


def listener(data):
    print("EVENT:", data)


event_manager.subscribe(
    "scheduler.system",
    listener
)


def system_job():

    print("SYSTEM JOB")
    return {
        "status": "online"
    }


scheduler.register(
    name="system",
    interval=2,
    callback=system_job,
    event="scheduler.system"
)

for i in range(5):

    print("=" * 60)
    print("TICK", i)

    scheduler.tick()

    time.sleep(1)

print("=" * 60)
print(event_manager.history())
print("=" * 60)
print(event_manager.stats())
