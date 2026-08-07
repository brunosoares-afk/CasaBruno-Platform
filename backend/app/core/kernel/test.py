import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from app.core.kernel.kernel import kernel

print(kernel.info())
print(kernel.health())
print(kernel.services())
print(kernel.events())
print(kernel.plugins())
print(kernel.scheduler())
