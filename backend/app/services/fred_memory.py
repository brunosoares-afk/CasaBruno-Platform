import json
import os
from pathlib import Path
from datetime import datetime, timedelta

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

    # Guardado por pessoa (Fase 6) — "liga ela" do Bruno não deve ser
    # afetado pelo que a Taiane mandou, e vice-versa. `person=None` cai
    # num slot "_global" único, pra canais que ainda não resolvem
    # identidade (voz/web hoje) continuarem funcionando como antes.

    def _bucket(self, person):
        key = person or "_global"
        return self.memory.setdefault(key, {})

    def remember(self, person, key, value):
        self._bucket(person)[key] = {
            "value": value,
            "updated": datetime.now().isoformat()
        }
        self.save()

    def recall(self, person, key):
        item = self._bucket(person).get(key)
        if item:
            return item.get("value")
        return None

    def recall_fresh(self, person, key, max_age_seconds):
        """Como recall(), mas descarta valores mais velhos que
        max_age_seconds — usado pra confirmações pendentes (Fase 8:
        "quer que eu apague?" -> "sim"), pra um "sim" de dias depois
        não reviver uma pergunta que já passou."""

        item = self._bucket(person).get(key)
        if not item:
            return None

        try:
            updated = datetime.fromisoformat(item["updated"])
        except (KeyError, ValueError):
            return item.get("value")

        if datetime.now() - updated > timedelta(seconds=max_age_seconds):
            return None

        return item.get("value")

    def forget(self, person, key):
        bucket = self._bucket(person)
        if key in bucket:
            del bucket[key]
            self.save()
            return True
        return False

    def all(self, person=None):
        if person is None:
            return self.memory
        return self._bucket(person)


memory = FredMemory()
