from fastapi import APIRouter, HTTPException, UploadFile

from app.services import detection_service, homeassistant_service

# Reconhecimento pela câmera de quem abre o painel web (não a câmera
# fixa da sala) — sem dependência de sessão de gerência, porque o
# painel principal (onde o personagem do Fred mora) não tem login,
# ver [[casa-bruno-web-face-recognition-2026-08-23]].
router = APIRouter(prefix="/web-recognition", tags=["Web Recognition"])


@router.post("")
async def recognize(file: UploadFile):
    try:
        image_bytes = await file.read()
        result = detection_service.recognize_face_in_image(image_bytes)
    except Exception as e:
        raise HTTPException(502, f"Falha ao falar com o serviço de reconhecimento: {e}")

    matches = [
        r for r in result.get("recognized", [])
        if r.get("name") not in (None, "Desconhecido")
    ]
    if matches:
        matches.sort(key=lambda r: r.get("confidence", 0))
        name = matches[0]["name"]
        homeassistant_service.report_recognized_person(name)
        return {"recognized": name}

    return {"recognized": None}
