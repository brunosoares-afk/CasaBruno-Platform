import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from main import app

print("=" * 60)
print(app.title)

print("=" * 60)
print("ROTAS")

for route in app.routes:
    path = getattr(route, "path", None)
    if path:
        print(path)
