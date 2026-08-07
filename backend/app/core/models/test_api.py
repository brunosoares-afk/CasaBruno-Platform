import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from app.core.models.api import api

print("=" * 60)
print(api.users())

print("=" * 60)
print(api.names())

print("=" * 60)
print(api.count())

print("=" * 60)
print(api.find(1))

print("=" * 60)
print(api.create("Maria"))

print("=" * 60)
print(api.users())

print("=" * 60)
print(api.delete(1))

print("=" * 60)
print(api.count())
