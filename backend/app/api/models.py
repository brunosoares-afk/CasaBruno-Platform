from fastapi import APIRouter

from app.core.models.api import api


router = APIRouter(
    prefix="/api/models",
    tags=["Models"]
)


@router.get("/users")
def users():
    return api.users()


@router.get("/names")
def names():
    return api.names()


@router.get("/count")
def count():
    return api.count()


@router.get("/find/{id}")
def find(id: int):
    return api.find(id)


@router.post("/create/{name}")
def create(name: str):
    return api.create(name)


@router.put("/update/{id}/{name}")
def update(id: int, name: str):
    return api.update(id, name)


@router.delete("/delete/{id}")
def delete(id: int):
    return api.delete(id)
