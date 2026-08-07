import json
from pathlib import Path


class Storage:

    VERSION = "2.0.0"

    def __init__(self):
        self.base = Path(__file__).resolve().parents[2]
        self.path = self.base / "storage"

        self.path.mkdir(
            parents=True,
            exist_ok=True
        )

    def file(self, name):
        return self.path / f"{name}.json"

    def exists(self, name):
        return self.file(name).exists()

    def read(self, name, default=None):

        if default is None:
            default = {}

        file = self.file(name)

        if not file.exists():
            return default

        with open(file, "r", encoding="utf-8") as f:
            return json.load(f)

    def write(self, name, data):

        with open(
            self.file(name),
            "w",
            encoding="utf-8"
        ) as f:
            json.dump(
                data,
                f,
                indent=4,
                ensure_ascii=False
            )

        return True

    def delete(self, name):

        file = self.file(name)

        if file.exists():
            file.unlink()
            return True

        return False

    def list(self):

        return sorted(
            [
                f.stem
                for f in self.path.glob("*.json")
            ]
        )

    def summary(self):

        return {
            "version": self.VERSION,
            "path": str(self.path),
            "files": self.list()
        }


storage = Storage()
