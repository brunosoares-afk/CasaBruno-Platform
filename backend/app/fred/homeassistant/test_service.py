import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from fred.homeassistant.client import homeassistant

print(homeassistant.info())
print(homeassistant.status())
print(homeassistant.health())
print(homeassistant.execute("restart"))
print(homeassistant.config())
