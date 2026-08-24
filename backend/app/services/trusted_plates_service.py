import json
import os
from pathlib import Path

# Lista de placas autorizadas a abrir o portão sozinhas — antes era um
# único TARGET_PLATE hardcoded dentro do container plate-detect-yoosee
# (OVI8D97), sem jeito de adicionar o carro da Taiane sem mexer em
# código. Agora o detector só reporta OCR bruto (plates_detected, ver
# [[casa-bruno-yoosee-object-detection-2026-08-23]]) e a decisão "essa
# placa é de alguém da casa" mora aqui, gerenciável por tela (Gerência
# → Placas), no mesmo padrão de app/data/fred_memory.json.

PLATES_FILE = str(Path(__file__).resolve().parents[1] / "data" / "trusted_plates.json")

PLATE_CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
MAX_DISTANCE = 2  # mesma tolerância a erro de OCR que o detector já usava


def _load() -> list[dict]:
    try:
        if os.path.exists(PLATES_FILE):
            with open(PLATES_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return []


def _save(plates: list[dict]) -> None:
    os.makedirs(os.path.dirname(PLATES_FILE), exist_ok=True)
    with open(PLATES_FILE, "w", encoding="utf-8") as f:
        json.dump(plates, f, indent=4, ensure_ascii=False)


def _normalize(plate: str) -> str:
    return "".join(c for c in plate.upper() if c in PLATE_CHARS)


def list_plates() -> list[dict]:
    return _load()


def add_plate(name: str, plate: str) -> dict:
    name = name.strip()
    plate = _normalize(plate)
    if not name or not plate:
        raise ValueError("name e plate são obrigatórios")

    plates = _load()
    plates = [p for p in plates if p["plate"] != plate]  # substitui se já existir
    plates.append({"name": name, "plate": plate})
    _save(plates)
    return {"name": name, "plate": plate}


def remove_plate(plate: str) -> bool:
    plate = _normalize(plate)
    plates = _load()
    remaining = [p for p in plates if p["plate"] != plate]
    if len(remaining) == len(plates):
        return False
    _save(remaining)
    return True


def _levenshtein(a: str, b: str) -> int:
    if len(a) < len(b):
        a, b = b, a
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def match(plates_detected: list[str]) -> dict | None:
    """Compara os textos de placa lidos nesse frame (podem ter ruído de
    OCR) contra a lista de confiança, com a mesma tolerância de distância
    que o detector usava pro alvo único. Devolve {name, plate} da
    primeira que bater, ou None."""
    trusted = _load()
    if not trusted:
        return None

    for text in plates_detected:
        for entry in trusted:
            if _levenshtein(text, entry["plate"]) <= MAX_DISTANCE:
                return entry
    return None
