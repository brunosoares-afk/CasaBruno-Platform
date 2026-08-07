import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from app.core.models.model import BaseModel


class UserModel(BaseModel):
    TABLE = "users"


users = UserModel()

print("=" * 60)
print(users.summary())

print("=" * 60)
print(users.all())

print("=" * 60)
print(users.find(1))

print("=" * 60)
print(users.exists(1))

print("=" * 60)
print(users.count())
