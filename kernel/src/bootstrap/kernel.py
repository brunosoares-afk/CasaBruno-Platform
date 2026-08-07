#!/usr/bin/env python3

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from core.kernel import CBOSKernel

if __name__ == "__main__":

    kernel = CBOSKernel()

    kernel.boot()
    kernel.info()
    kernel.shutdown()
