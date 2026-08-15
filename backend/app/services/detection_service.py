import requests

FACE_URL = "http://127.0.0.1:8091/status"
PLATE_URL = "http://127.0.0.1:8092/status"
TIMEOUT = 5


def get_face_status() -> dict | None:
    try:
        r = requests.get(FACE_URL, timeout=TIMEOUT)
        r.raise_for_status()
        return r.json()
    except Exception:
        return None


def get_plate_status() -> dict | None:
    try:
        r = requests.get(PLATE_URL, timeout=TIMEOUT)
        r.raise_for_status()
        return r.json()
    except Exception:
        return None


def recognized_person_name(face_status: dict | None) -> str:
    """Mesma lógica do value_template que o HA usava pro sensor
    'iCSee Pessoa Reconhecida': ignora 'Desconhecido', ordena por
    confiança (ascendente, mesmo comportamento de antes) e pega o
    primeiro; sem match nenhum, 'Ninguém'."""

    if not face_status:
        return "Ninguém"

    matches = [
        r for r in face_status.get("recognized", [])
        if r.get("name") != "Desconhecido"
    ]

    if not matches:
        return "Ninguém"

    matches.sort(key=lambda r: r.get("confidence", 0))
    return matches[0]["name"]
