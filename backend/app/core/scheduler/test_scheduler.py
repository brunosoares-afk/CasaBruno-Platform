import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from app.core.scheduler.scheduler import scheduler


def job1():
    print("JOB 1")


def job2():
    print("JOB 2")


scheduler.register("system", 30, job1)
scheduler.register("docker", 60, job2)

print(scheduler.list())
print()

print(scheduler.run("system"))
print()

print([scheduler.run(name) for name in scheduler.list()])
print()

print(scheduler.list())

scheduler.disable("docker")

print()

print([scheduler.run(name) for name in scheduler.list()])
print()

print(scheduler.list())
