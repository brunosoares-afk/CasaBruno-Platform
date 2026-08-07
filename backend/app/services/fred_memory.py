import json
import os
from pathlib import Path
from datetime import datetime

MEMORY_FILE = str(Path(__file__).resolve().parents[1] / "data" / "fred_memory.json")


class FredMemory:

    def __init__(self):
        self.memory = {}
        self.load()

    def load(self):
        try:
            if os.path.exists(MEMORY_FILE):
                with open(MEMORY_FILE, "r", encoding="utf-8") as file:
                    self.memory = json.load(file)
        except Exception:
            self.memory = {}

    def save(self):
        try:
            os.makedirs(os.path.dirname(MEMORY_FILE), exist_ok=True)
            with open(MEMORY_FILE, "w", encoding="utf-8") as file:
                json.dump(self.memory, file, indent=4, ensure_ascii=False)
        except Exception:
            pass

    def remember(self, key, value):
        self.memory[key] = {
            "value": value,
            "updated": datetime.now().isoformat()
        }
        self.save()

    def recall(self, key):
        item = self.memory.get(key)
        if item:
            return item.get("value")
        return None

    def forget(self, key):
        if key in self.memory:
            del self.memory[key]
            self.save()
            return True
        return False

    def all(self):
        return self.memory


memory = FredMemory()
