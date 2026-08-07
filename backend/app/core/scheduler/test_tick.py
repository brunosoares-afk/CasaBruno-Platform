import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from app.core.scheduler.scheduler import scheduler


def fast():
    print("FAST")


def slow():
    print("SLOW")


scheduler.register("fast", 2, fast)
scheduler.register("slow", 5, slow)

for i in range(8):

    print("=" * 50)
    print("TICK", i)

    scheduler.tick()

    print(scheduler.list())

    time.sleep(1)
