import shutil
import time
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel

from app.api.auth import require_gerencia_session
from app.core.config.config import config

router = APIRouter(
    prefix="/api/uploads",
    tags=["Uploads"]
)

UPLOAD_DIR = Path("/opt/CasaBruno-Platform/backend/uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".svg"}


def _floor_plan_response():
    meta = config.get("floor_plan")
    if not meta or not (UPLOAD_DIR / meta["filename"]).exists():
        return {"exists": False, "url": None, "away_url": None}

    version = meta.get("updated_at", "")
    response = {"exists": True, "url": f"/uploads/{meta['filename']}?v={version}", "away_url": None}

    # Variante "carro fora" — arquivo estático editado manualmente
    # (mesmo nome + sufixo _no_car), pra planta mostrar a garagem vazia
    # quando o POCO X8 do Bruno não está em casa. Se a planta for trocada
    # por uma imagem nova, esse arquivo fica desatualizado até alguém
    # gerar um novo (não é regenerado automaticamente no upload).
    stem = Path(meta["filename"]).stem
    suffix = Path(meta["filename"]).suffix
    away_path = UPLOAD_DIR / f"{stem}_no_car{suffix}"
    if away_path.exists():
        response["away_url"] = f"/uploads/{away_path.name}?v={version}"

    return response


@router.get("/floor-plan/info")
def floor_plan_info():
    return _floor_plan_response()


@router.post("/floor-plan", dependencies=[Depends(require_gerencia_session)])
async def upload_floor_plan(file: UploadFile = File(...)):
    ext = Path(file.filename or "").suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Formato não suportado (use PNG, JPG, WEBP ou SVG)")

    old_meta = config.get("floor_plan")
    if old_meta:
        old_path = UPLOAD_DIR / old_meta["filename"]
        if old_path.exists():
            old_path.unlink()

    filename = f"floor_plan{ext}"
    dest = UPLOAD_DIR / filename
    with dest.open("wb") as out:
        shutil.copyfileobj(file.file, out)

    config.set("floor_plan", {"filename": filename, "updated_at": str(int(time.time()))})
    return _floor_plan_response()


@router.delete("/floor-plan", dependencies=[Depends(require_gerencia_session)])
def delete_floor_plan():
    meta = config.get("floor_plan")
    if meta:
        path = UPLOAD_DIR / meta["filename"]
        if path.exists():
            path.unlink()
        config.delete("floor_plan")
    return {"exists": False, "url": None}


# ======================================================
# MARCADORES DA PLANTA (ícones que reagem ao estado real)
# ======================================================

class FloorPlanMarker(BaseModel):

    id: str
    entity_id: str
    label: str | None = None
    icon: str
    x_pct: float
    y_pct: float
    type: str = "state"
    active_states: list[str] = ["on"]
    anim_style: str = "glow"
    hide_when_inactive: bool = False


class FloorPlanMarkersUpdate(BaseModel):

    markers: list[FloorPlanMarker]


@router.get("/floor-plan/markers")
def get_floor_plan_markers():
    return {"markers": config.get("floor_plan_markers") or []}


@router.put("/floor-plan/markers", dependencies=[Depends(require_gerencia_session)])
def set_floor_plan_markers(data: FloorPlanMarkersUpdate):
    markers = [m.dict() for m in data.markers]
    config.set("floor_plan_markers", markers)
    return {"markers": markers}
