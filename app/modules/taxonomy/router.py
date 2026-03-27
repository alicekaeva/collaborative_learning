from typing import List
from fastapi import APIRouter, Depends

from app.api.deps import DBDep, require_roles
from app.models.user import User
from app.core.exceptions import NotFoundError
from app.modules.taxonomy import repository as repo
from app.modules.taxonomy.schemas.category import CategoryCreate, CategoryUpdate, CategoryRead
from app.modules.taxonomy.schemas.tag import TagCreate, TagUpdate, TagRead

categories_router = APIRouter(prefix="/categories", tags=["categories"])
tags_router = APIRouter(prefix="/tags", tags=["tags"])


# ------------------------------------------------------------------ Categories

@categories_router.get("/", response_model=List[CategoryRead])
async def list_categories(db: DBDep):
    return await repo.get_all_categories(db)


@categories_router.post("/", response_model=CategoryRead, status_code=201)
async def create_category(
    data: CategoryCreate,
    db: DBDep,
    _: User = Depends(require_roles("ROLE_ADMIN")),
):
    return await repo.create_category(db, data)


@categories_router.get("/{category_id}", response_model=CategoryRead)
async def get_category(category_id: int, db: DBDep):
    cat = await repo.get_category_by_id(db, category_id)
    if not cat:
        raise NotFoundError("Категория не найдена")
    return cat


@categories_router.patch("/{category_id}", response_model=CategoryRead)
async def update_category(
    category_id: int,
    data: CategoryUpdate,
    db: DBDep,
    _: User = Depends(require_roles("ROLE_ADMIN")),
):
    cat = await repo.get_category_by_id(db, category_id)
    if not cat:
        raise NotFoundError("Категория не найдена")
    return await repo.update_category(db, cat, data)


@categories_router.get("/{category_id}/tags", response_model=List[TagRead])
async def list_category_tags(category_id: int, db: DBDep):
    tags = await repo.get_tags_by_category(db, category_id)
    return [
        TagRead(
            id=t.id, name=t.name, category_id=t.category_id,
            category_name=t.category.name if t.category else None,
        )
        for t in tags
    ]


@categories_router.delete("/{category_id}", status_code=204)
async def delete_category(
    category_id: int,
    db: DBDep,
    _: User = Depends(require_roles("ROLE_ADMIN")),
):
    cat = await repo.get_category_by_id(db, category_id)
    if not cat:
        raise NotFoundError("Категория не найдена")
    await repo.delete_category(db, cat)


# ------------------------------------------------------------------ Tags

@tags_router.get("/", response_model=List[TagRead])
async def list_tags(db: DBDep):
    tags = await repo.get_all_tags(db)
    return [
        TagRead(
            id=t.id, name=t.name, category_id=t.category_id,
            category_name=t.category.name if t.category else None,
        )
        for t in tags
    ]


@tags_router.post("/", response_model=TagRead, status_code=201)
async def create_tag(
    data: TagCreate,
    db: DBDep,
    _: User = Depends(require_roles("ROLE_ADMIN")),
):
    return await repo.create_tag(db, data)


@tags_router.get("/{tag_id}", response_model=TagRead)
async def get_tag(tag_id: int, db: DBDep):
    tag = await repo.get_tag_by_id(db, tag_id)
    if not tag:
        raise NotFoundError("Тег не найден")
    return TagRead(
        id=tag.id, name=tag.name, category_id=tag.category_id,
        category_name=tag.category.name if tag.category else None,
    )


@tags_router.patch("/{tag_id}", response_model=TagRead)
async def update_tag(
    tag_id: int,
    data: TagUpdate,
    db: DBDep,
    _: User = Depends(require_roles("ROLE_ADMIN")),
):
    tag = await repo.get_tag_by_id(db, tag_id)
    if not tag:
        raise NotFoundError("Тег не найден")
    return await repo.update_tag(db, tag, data)


@tags_router.delete("/{tag_id}", status_code=204)
async def delete_tag(
    tag_id: int,
    db: DBDep,
    _: User = Depends(require_roles("ROLE_ADMIN")),
):
    tag = await repo.get_tag_by_id(db, tag_id)
    if not tag:
        raise NotFoundError("Тег не найден")
    await repo.delete_tag(db, tag)
