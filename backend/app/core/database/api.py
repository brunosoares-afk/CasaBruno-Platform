from app.core.database.database import database


class DatabaseAPI:

    def info(self):
        return database.summary()

    def execute(self, sql, params=()):
        return {
            "success": database.execute(sql, params)
        }

    def query(self, sql, params=()):
        return database.query(sql, params)

    def value(self, sql, params=()):
        return database.value(sql, params)

    def tables(self):
        rows = database.query(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        )

        return [r["name"] for r in rows]


api = DatabaseAPI()
