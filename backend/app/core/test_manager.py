import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.core.service_manager import manager

print(manager.services())
print(manager.info("system"))
print(manager.health("system"))
print(manager.info("docker"))
print(manager.health("docker"))
