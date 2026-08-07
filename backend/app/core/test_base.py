import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.core.base_service import BaseService


class TestService(BaseService):
    NAME = "test"


service = TestService()

print(service.info())
print(service.status())
print(service.health())
print(service.execute("run"))
print(service.config())
