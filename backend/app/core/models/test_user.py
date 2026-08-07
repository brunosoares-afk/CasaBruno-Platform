import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from app.core.models.user import user

print("=" * 60)
print(user.summary())

print("=" * 60)
print(user.create("Carlos"))

print("=" * 60)
print(user.find(1))

print("=" * 60)
print(user.names())

print("=" * 60)
print(user.count())
