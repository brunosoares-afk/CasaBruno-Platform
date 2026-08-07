import sqlite3
from pathlib import Path


class Database:

    VERSION = "2.0.0"

    def __init__(self):
        self.base = Path(__file__).resolve().parents[2]

        self.path = self.base / "storage"
        self.path.mkdir(
            parents=True,
            exist_ok=True
        )

        self.file = self.path / "casabruno.db"

    def connect(self):
        conn = sqlite3.connect(self.file)
        conn.row_factory = sqlite3.Row
        return conn

    def execute(self, sql, params=()):
        conn = self.connect()

        try:
            cur = conn.cursor()
            cur.execute(sql, params)
            conn.commit()
            return True

        finally:
            conn.close()

    def query(self, sql, params=()):
        conn = self.connect()

        try:
            cur = conn.cursor()
            cur.execute(sql, params)

            rows = cur.fetchall()

            return [
                dict(row)
                for row in rows
            ]

        finally:
            conn.close()

    def value(self, sql, params=()):
        rows = self.query(sql, params)

        if not rows:
            return None

        first = rows[0]

        if not first:
            return None

        return next(iter(first.values()))

    def summary(self):
        return {
            "version": self.VERSION,
            "database": str(self.file),
            "exists": self.file.exists()
        }


database = Database()
