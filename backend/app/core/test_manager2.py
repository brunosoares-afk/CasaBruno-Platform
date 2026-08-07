import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.core.service_manager2 import manager2

print(manager2.services())

print()

for name in manager2.services():
    print(name)
    print(manager2.info(name))
    print(manager2.status(name))
    print(manager2.health(name))
    print("---")

print(manager2.reload())
