import requests

FACE_BASE_URL = "http://127.0.0.1:8091"
FACE_URL = f"{FACE_BASE_URL}/status"
PLATE_URL = "http://127.0.0.1:8092/status"
TIMEOUT = 5
ENROLL_TIMEOUT = 15  # captura/treino demoram mais que uma checagem de status


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


def recognize_face_in_image(image_bytes: bytes) -> dict:
    """Manda um frame (câmera do dispositivo de quem abriu o painel web,
    não a icsee fixa) pro mesmo reconhecedor LBPH já treinado, ver
    [[casa-bruno-web-face-recognition-2026-08-23]]."""
    r = requests.post(
        f"{FACE_BASE_URL}/recognize",
        files={"file": ("frame.jpg", image_bytes, "image/jpeg")},
        timeout=TIMEOUT,
    )
    r.raise_for_status()
    return r.json()


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


# ==========================================================
# CADASTRO DE ROSTO — proxy fino pro face-detect-icsee (:8091), que já
# tem a API certa pra isso (captura da câmera ao vivo, recorta,
# retreina o modelo LBPH e recarrega sozinho, sem precisar reiniciar
# nada). Usado pela tela de cadastro em Gerência, 2026-08-21.
# ==========================================================

def list_enrolled_people() -> dict:
    """{nome: quantidade_de_fotos}"""
    r = requests.get(f"{FACE_BASE_URL}/people", timeout=TIMEOUT)
    r.raise_for_status()
    return r.json()


def enroll_capture(name: str) -> dict:
    """Captura UM rosto da câmera ao vivo pra esse nome — a pessoa
    precisa estar na frente da câmera nesse instante. Chamar várias
    vezes (10-20x, variando ângulo/expressão) antes de treinar."""
    r = requests.post(f"{FACE_BASE_URL}/enroll/capture", params={"name": name}, timeout=ENROLL_TIMEOUT)
    r.raise_for_status()
    return r.json()


def train_model() -> dict:
    r = requests.post(f"{FACE_BASE_URL}/train", timeout=ENROLL_TIMEOUT)
    r.raise_for_status()
    return r.json()


def delete_person(name: str) -> dict:
    r = requests.delete(f"{FACE_BASE_URL}/people/{name}", timeout=TIMEOUT)
    r.raise_for_status()
    return r.json()
