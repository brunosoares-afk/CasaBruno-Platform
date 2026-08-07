import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.core.discovery import discovery

for service in discovery.discover():
    print(service.NAME)
