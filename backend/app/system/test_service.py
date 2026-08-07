import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from system.system import system

print(system.info())
print(system.status())
print(system.health())
print(system.config())
print(system.execute())
print(system.system_info())
