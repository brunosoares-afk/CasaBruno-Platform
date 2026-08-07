import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from app.core.bootstrap.api import api

print("=" * 60)
print(api.info())

print("=" * 60)
print(api.start())

print("=" * 60)
print(api.discovery())

print("=" * 60)
print(api.services())

print("=" * 60)
print(api.plugins())

print("=" * 60)
print(api.restart())

print("=" * 60)
print(api.stop())
