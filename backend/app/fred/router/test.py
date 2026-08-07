import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))

from router.router import router

print(router.route("acender luz"))
print(router.route("temperatura"))
print(router.route("docker"))
print(router.route("teste"))
