from typing import List
from fastapi import APIRouter, Depends

from app.api.deps import DBDep, require_roles
from app.models.user import User
from app.core.exceptions import NotFoundError
from app.crud import tag as tag_crud
from app.schemas.tag import TagCreate, TagUpdate, TagRead

router = APIRouter(prefix="/tags", tags=["tags"])


@router.get("/", response_model=List[TagRead])
async def list_tags(db: DBDep):
    tags = await tag_crud.get_all(db)
    return [
        TagRead(id=t.id, name=t.name, category_id=t.category_id,
                category_name=t.category.name if t.category else None)
        for t in tags
    ]


@router.post("/", response_model=TagRead, status_code=201)
async def create_tag(
    data: TagCreate,
    db: DBDep,
    _: User = Depends(require_roles("ROLE_ADMIN")),
):
    return await tag_crud.create(db, data)


@router.get("/{tag_id}", response_model=TagRead)
async def get_tag(tag_id: int, db: DBDep):
    tag = await tag_crud.get_by_id(db, tag_id)
    if not tag:
        raise NotFoundError("Тег не найден")
    return TagRead(
        id=tag.id, name=tag.name, category_id=tag.category_id,
        category_name=tag.category.name if tag.category else None,
    )


@router.patch("/{tag_id}", response_model=TagRead)
async def update_tag(
    tag_id: int,
    data: TagUpdate,
    db: DBDep,
    _: User = Depends(require_roles("ROLE_ADMIN")),
):
    tag = await tag_crud.get_by_id(db, tag_id)
    if not tag:
        raise NotFoundError("Тег не найден")
    return await tag_crud.update_tag(db, tag, data)


@router.delete("/{tag_id}", status_code=204)
async def delete_tag(
    tag_id: int,
    db: DBDep,
    _: User = Depends(require_roles("ROLE_ADMIN")),
):
    tag = await tag_crud.get_by_id(db, tag_id)
    if not tag:
        raise NotFoundError("Тег не найден")
    await tag_crud.delete(db, tag)
