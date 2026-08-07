import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from main import app
from app.core.kernel.kernel import kernel


print("=" * 60)
print(app.title)

print("=" * 60)
print("ROTAS")

for route in app.routes:
    path = getattr(route, "path", None)
    if path:
        print(path)

print("=" * 60)
print(kernel.info())

print("=" * 60)
print(kernel.registry().list())

print("=" * 60)
print(kernel.services().services())

print("=" * 60)
print(kernel.plugins().list())

print("=" * 60)
print(kernel.events().summary())

print("=" * 60)
print(kernel.scheduler().stats())

print("=" * 60)
print(kernel.health())
