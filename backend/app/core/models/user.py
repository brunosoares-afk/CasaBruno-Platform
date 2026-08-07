from app.core.models.model import BaseModel


class UserModel(BaseModel):

    TABLE = "users"

    def create(self, name):

        self.db.execute(
            "INSERT INTO users(name) VALUES(?)",
            (name,)
        )

        return self.db.value(
            "SELECT last_insert_rowid()"
        )

    def update(self, id, name):

        return self.db.execute(
            "UPDATE users SET name=? WHERE id=?",
            (name, id)
        )

    def names(self):

        rows = self.db.query(
            "SELECT name FROM users ORDER BY id"
        )

        return [r["name"] for r in rows]


user = UserModel()
