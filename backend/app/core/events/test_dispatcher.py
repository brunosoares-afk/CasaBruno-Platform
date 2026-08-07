import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from app.core.events.dispatcher import dispatcher


def callback_a(data):
    print("A:", data)


def callback_b(data):
    print("B:", data)


dispatcher.register("system.start", callback_a)
dispatcher.register("system.start", callback_b)

print(dispatcher.dispatch("system.start", {"status": "online"}))
print()

print(dispatcher.events())
print()

print(dispatcher.listeners_count())
print()

dispatcher.unregister("system.start", callback_b)

print(dispatcher.dispatch("system.start", {"status": "offline"}))
print()

print(dispatcher.listeners_count())
