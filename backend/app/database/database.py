import sqlite3

from pathlib import Path

from config.settings import settings


DB_PATH = Path(settings.DATABASE_PATH)

DB_PATH.parent.mkdir(
    parents=True,
    exist_ok=True
)


class Database:

    def __init__(self):

        self.connection = sqlite3.connect(
            DB_PATH,
            check_same_thread=False
        )

        self.connection.row_factory = sqlite3.Row

        self.create_tables()

    def create_tables(self):

        cursor = self.connection.cursor()

        cursor.execute("""

        CREATE TABLE IF NOT EXISTS events (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            timestamp TEXT,

            event TEXT,

            source TEXT,

            data TEXT

        )

        """)

        cursor.execute("""

        CREATE TABLE IF NOT EXISTS logs (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            timestamp TEXT,

            level TEXT,

            source TEXT,

            message TEXT

        )

        """)

        cursor.execute("""

        CREATE TABLE IF NOT EXISTS registry (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            entity_id TEXT,

            friendly_name TEXT,

            domain TEXT,

            last_seen TEXT

        )

        """)

        self.connection.commit()

    def execute(self, query, values=()):

        cursor = self.connection.cursor()

        cursor.execute(query, values)

        self.connection.commit()

        return cursor

    def fetchall(self, query, values=()):

        cursor = self.connection.cursor()

        cursor.execute(query, values)

        return [dict(r) for r in cursor.fetchall()]

    def fetchone(self, query, values=()):

        cursor = self.connection.cursor()

        cursor.execute(query, values)

        row = cursor.fetchone()

        return dict(row) if row else None


db = Database()
