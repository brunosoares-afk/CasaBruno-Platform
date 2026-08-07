import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from app.core.database.database import database

print("=" * 60)
print(database.summary())

database.execute("""
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT
)
""")

print("=" * 60)
print(database.table_exists("users"))

database.execute(
    "INSERT INTO users(name) VALUES(?)",
    ("Bruno",)
)

print("=" * 60)
print(database.query("SELECT * FROM users"))

print("=" * 60)
print(database.scalar("SELECT COUNT(*) FROM users"))
