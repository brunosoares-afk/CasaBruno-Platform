import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from app.core.scheduler.manager import scheduler_manager
from app.core.events.event_manager import event_manager


def listener(data):
    print("EVENT:", data)


event_manager.subscribe("job.system", listener)
event_manager.subscribe("job.docker", listener)


def system_job():
    print("SYSTEM")
    return {"status": "online"}


def docker_job():
    print("DOCKER")
    return {"containers": 10}


scheduler_manager.register(
    "system",
    2,
    system_job,
    event="job.system"
)

scheduler_manager.register(
    "docker",
    3,
    docker_job,
    event="job.docker"
)

for i in range(7):

    print("=" * 60)
    print("TICK", i)

    scheduler_manager.tick()

    time.sleep(1)

print("=" * 60)
print(scheduler_manager.list())
print("=" * 60)
print(scheduler_manager.stats())
print("=" * 60)
print(event_manager.history())
