import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from app.core.storage.api import api

print("=" * 60)
print(api.info())

print("=" * 60)
print(api.write(
    "usuarios",
    {
        "admin": True
    }
))

print("=" * 60)
print(api.read("usuarios"))

print("=" * 60)
print(api.exists("usuarios"))

print("=" * 60)
print(api.list())

print("=" * 60)
print(api.delete("usuarios"))

print("=" * 60)
print(api.list())
