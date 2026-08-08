import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from app.core.database.database import database

# Redireciona para um sqlite temporário: este teste nunca deve escrever em
# backend/app/storage/casabruno.db, que é o banco real da aplicação.
database.path = Path(tempfile.mkdtemp())
database.file = database.path / "test.db"

print("=" * 60)
print(database.summary())

database.execute("""
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT
)
""")

print("=" * 60)
print(database.query(
    "SELECT name FROM sqlite_master WHERE type='table' AND name='users'"
))

database.execute(
    "INSERT INTO users(name) VALUES(?)",
    ("Bruno",)
)

print("=" * 60)
print(database.query("SELECT * FROM users"))

print("=" * 60)
print(database.value("SELECT COUNT(*) FROM users"))
