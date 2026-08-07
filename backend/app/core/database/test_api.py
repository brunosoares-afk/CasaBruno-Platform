import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from app.core.database.api import api

print("=" * 60)
print(api.info())

print("=" * 60)
print(api.execute("""
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT
)
"""))

print("=" * 60)
print(api.execute(
    "INSERT INTO users(name) VALUES(?)",
    ("Bruno",)
))

print("=" * 60)
print(api.query("SELECT * FROM users"))

print("=" * 60)
print(api.value("SELECT COUNT(*) FROM users"))

print("=" * 60)
print(api.tables())
