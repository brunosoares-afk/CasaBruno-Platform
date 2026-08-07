from app.core.models.user import user


class ModelsAPI:

    def users(self):
        return user.all()

    def names(self):
        return user.names()

    def count(self):
        return user.count()

    def find(self, id):
        return user.find(id)

    def create(self, name):
        return {
            "id": user.create(name)
        }

    def update(self, id, name):
        return {
            "success": user.update(id, name)
        }

    def delete(self, id):
        return {
            "success": user.delete(id)
        }


api = ModelsAPI()
