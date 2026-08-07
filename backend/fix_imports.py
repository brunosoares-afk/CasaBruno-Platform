from pathlib import Path
import re

ROOT = Path("/opt/CasaBruno-Platform/backend/app")

REPLACEMENTS = {
    r"\bfrom services\.": "from app.services.",
    r"\bimport services\.": "import app.services.",

    r"\bfrom core\.": "from app.core.",
    r"\bimport core\.": "import app.core.",

    r"\bfrom routers\.": "from app.routers.",
    r"\bimport routers\.": "import app.routers.",

    r"\bfrom api\.": "from app.api.",
    r"\bimport api\.": "import app.api.",

    r"\bfrom integrations\.": "from app.integrations.",
    r"\bimport integrations\.": "import app.integrations.",
}


count_files = 0
count_changes = 0

for file in ROOT.rglob("*.py"):

    text = file.read_text(encoding="utf-8")

    original = text

    for old, new in REPLACEMENTS.items():
        text = re.sub(old, new, text)

    if text != original:
        file.write_text(text, encoding="utf-8")
        count_files += 1
        count_changes += 1
        print(f"Corrigido: {file}")

print()
print("========================================")
print(f"Arquivos alterados : {count_files}")
print(f"Total de alterações: {count_changes}")
print("========================================")
