import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from app.core.config.config import config

# Redireciona para um arquivo temporário: este teste nunca deve ler nem
# escrever em backend/app/config.json, que guarda credenciais reais.
config.file = Path(tempfile.mkdtemp()) / "config.json"
config.data = {}
config.save()

print("=" * 60)
print(config.summary())

print("=" * 60)
print(config.all())

print("=" * 60)
print(config.get("application"))

print("=" * 60)
print(config.get("homeassistant"))

print("=" * 60)
config.set("application", {"name": "CasaBruno Platform", "version": "2.0.0"})

print(config.get("application"))
