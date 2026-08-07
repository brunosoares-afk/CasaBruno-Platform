from app.core.database.database import database


class BaseModel:

    TABLE = ""

    def __init__(self):
        self.db = database

    def all(self):
        sql = f"SELECT * FROM {self.TABLE}"
        return self.db.query(sql)

    def count(self):
        sql = f"SELECT COUNT(*) FROM {self.TABLE}"
        return self.db.value(sql)

    def find(self, id):
        sql = f"SELECT * FROM {self.TABLE} WHERE id=?"
        rows = self.db.query(sql, (id,))

        if rows:
            return rows[0]

        return None

    def delete(self, id):
        sql = f"DELETE FROM {self.TABLE} WHERE id=?"
        return self.db.execute(sql, (id,))

    def exists(self, id):
        return self.find(id) is not None

    def summary(self):
        return {
            "table": self.TABLE,
            "count": self.count()
        }
