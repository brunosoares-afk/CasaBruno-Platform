import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.core.registry2 import registry2

print(registry2.list())

print()

for name in registry2.list():
    service = registry2.get(name)
    print(name)
    print(service.info())

print()

print(registry2.reload())
