from fastapi import APIRouter
from pydantic import BaseModel

from app.services import memory_service

router = APIRouter(
    tags=["KNOWLEDGE"]
)


# ======================================================
# MODELO
# ======================================================

class KnowledgeCreate(BaseModel):

    category: str
    content: str
    label: str | None = None


class KnowledgeUpdate(BaseModel):

    label: str | None = None
    content: str | None = None


# ======================================================
# CRUD
# ======================================================

@router.get("/knowledge")
def list_knowledge(category: str | None = None, search: str | None = None):

    if search:
        return {"items": memory_service.search_knowledge(search, limit=20)}

    return {"items": memory_service.list_knowledge(category)}


@router.post("/knowledge")
def create_knowledge(data: KnowledgeCreate):

    knowledge_id = memory_service.add_knowledge(
        category=data.category,
        content=data.content,
        label=data.label,
        source="manual",
    )

    return {"id": knowledge_id}


@router.put("/knowledge/{knowledge_id}")
def update_knowledge(knowledge_id: int, data: KnowledgeUpdate):

    updated = memory_service.update_knowledge(
        knowledge_id,
        label=data.label,
        content=data.content,
    )

    if updated is None:
        return {"success": False, "message": "Fato não encontrado."}

    return {"success": True}


@router.delete("/knowledge/{knowledge_id}")
def delete_knowledge(knowledge_id: int):

    memory_service.delete_knowledge(knowledge_id)

    return {"success": True}
