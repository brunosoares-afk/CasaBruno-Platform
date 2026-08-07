import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from fred.network.client import network

print(network.info())
print(network.status())
print(network.health())
print(network.execute("scan"))
print(network.config())
