import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from app.core.config.api import api

print("=" * 60)
print(api.info())

print("=" * 60)
print(api.all())

print("=" * 60)
print(api.get("application"))

print("=" * 60)
print(api.set(
    "application",
    {
        "name": "CasaBruno Platform",
        "version": "2.0.0"
    }
))

print("=" * 60)
print(api.reload())

print("=" * 60)
print(api.save())
