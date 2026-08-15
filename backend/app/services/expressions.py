import json
import random
from pathlib import Path

EXPRESSIONS_PATH = Path(__file__).resolve().parents[1] / "data" / "fred_expressions.json"

try:
    with open(EXPRESSIONS_PATH, encoding="utf-8") as f:
        EXPRESSIONS = json.load(f)
except Exception:
    EXPRESSIONS = {}


def pick(category: str, default: str = "") -> str:
    options = EXPRESSIONS.get(category)
    if not options:
        return default
    return random.choice(options)


def sample_all(per_category: int = 1) -> str:
    if not EXPRESSIONS:
        return ""
    picked = []
    for options in EXPRESSIONS.values():
        if options:
            picked.extend(random.sample(options, min(per_category, len(options))))
    if not picked:
        return ""
    return ", ".join(f'"{p}"' for p in picked)
