from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate


async def get_by_id(db: AsyncSession, category_id: int) -> Optional[Category]:
    result = await db.execute(select(Category).where(Category.id == category_id))
    return result.scalar_one_or_none()


async def get_all(db: AsyncSession) -> List[Category]:
    result = await db.execute(select(Category))
    return list(result.scalars().all())


async def create(db: AsyncSession, data: CategoryCreate) -> Category:
    category = Category(name=data.name)
    db.add(category)
    await db.commit()
    await db.refresh(category)
    return category


async def update_category(db: AsyncSession, category: Category, data: CategoryUpdate) -> Category:
    if data.name is not None:
        category.name = data.name
    await db.commit()
    await db.refresh(category)
    return category


async def delete(db: AsyncSession, category: Category) -> None:
    await db.delete(category)
    await db.commit()
