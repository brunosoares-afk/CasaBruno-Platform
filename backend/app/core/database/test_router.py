import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from app.api.database import router

print("=" * 60)
print(router.prefix)

print("=" * 60)

for route in router.routes:
    print(route.path)

