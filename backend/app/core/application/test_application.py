import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from app.core.application.api import api

print("=" * 60)
print(api.info())

print("=" * 60)
print(api.start())

print("=" * 60)
print(api.kernel())

print("=" * 60)
print(api.restart())

print("=" * 60)
print(api.stop())
