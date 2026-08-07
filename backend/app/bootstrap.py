import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

import app.core.register_services

from app.core.kernel.kernel import kernel

print(kernel.info())
