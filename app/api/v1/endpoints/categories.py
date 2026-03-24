from typing import List
from fastapi import APIRouter, Depends

from app.api.deps import DBDep, require_roles
from app.models.user import User
from app.core.exceptions import NotFoundError
from app.crud import category as category_crud
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryRead
from app.schemas.common import Message

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("/", response_model=List[CategoryRead])
async def list_categories(db: DBDep):
    return await category_crud.get_all(db)


@router.post("/", response_model=CategoryRead, status_code=201)
async def create_category(
    data: CategoryCreate,
    db: DBDep,
    _: User = Depends(require_roles("ROLE_ADMIN")),
):
    return await category_crud.create(db, data)


@router.get("/{category_id}", response_model=CategoryRead)
async def get_category(category_id: int, db: DBDep):
    cat = await category_crud.get_by_id(db, category_id)
    if not cat:
        raise NotFoundError("Категория не найдена")
    return cat


@router.patch("/{category_id}", response_model=CategoryRead)
async def update_category(
    category_id: int,
    data: CategoryUpdate,
    db: DBDep,
    _: User = Depends(require_roles("ROLE_ADMIN")),
):
    cat = await category_crud.get_by_id(db, category_id)
    if not cat:
        raise NotFoundError("Категория не найдена")
    return await category_crud.update_category(db, cat, data)


@router.delete("/{category_id}", response_model=Message)
async def delete_category(
    category_id: int,
    db: DBDep,
    _: User = Depends(require_roles("ROLE_ADMIN")),
):
    cat = await category_crud.get_by_id(db, category_id)
    if not cat:
        raise NotFoundError("Категория не найдена")
    await category_crud.delete(db, cat)
    return Message(detail="Категория удалена")
