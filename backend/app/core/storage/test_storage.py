import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from app.core.storage.storage import storage

print("=" * 60)
print(storage.summary())

storage.write(
    "teste",
    {
        "ok": True,
        "version": "2.0.0"
    }
)

print("=" * 60)
print(storage.read("teste"))

print("=" * 60)
print(storage.list())

storage.delete("teste")

print("=" * 60)
print(storage.list())
