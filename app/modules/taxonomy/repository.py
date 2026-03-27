from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.taxonomy.models.category import Category
from app.modules.taxonomy.models.tag import Tag
from app.modules.taxonomy.schemas.category import CategoryCreate, CategoryUpdate
from app.modules.taxonomy.schemas.tag import TagCreate, TagUpdate


# ------------------------------------------------------------------ Category

async def get_category_by_id(db: AsyncSession, category_id: int) -> Optional[Category]:
    result = await db.execute(select(Category).where(Category.id == category_id))
    return result.scalar_one_or_none()


async def get_all_categories(db: AsyncSession) -> List[Category]:
    result = await db.execute(select(Category))
    return list(result.scalars().all())


async def create_category(db: AsyncSession, data: CategoryCreate) -> Category:
    category = Category(name=data.name)
    db.add(category)
    await db.commit()
    await db.refresh(category)
    return category


async def update_category(db: AsyncSession, category: Category, data: CategoryUpdate) -> Category:
    category.name = data.name
    await db.commit()
    await db.refresh(category)
    return category


async def delete_category(db: AsyncSession, category: Category) -> None:
    await db.delete(category)
    await db.commit()


# ------------------------------------------------------------------ Tag

async def get_tag_by_id(db: AsyncSession, tag_id: int) -> Optional[Tag]:
    result = await db.execute(select(Tag).where(Tag.id == tag_id))
    return result.scalar_one_or_none()


async def get_all_tags(db: AsyncSession) -> List[Tag]:
    result = await db.execute(select(Tag))
    return list(result.scalars().all())


async def get_tags_by_category(db: AsyncSession, category_id: int) -> List[Tag]:
    result = await db.execute(select(Tag).where(Tag.category_id == category_id))
    return list(result.scalars().all())


async def create_tag(db: AsyncSession, data: TagCreate) -> Tag:
    tag = Tag(name=data.name, category_id=data.category_id)
    db.add(tag)
    await db.commit()
    await db.refresh(tag)
    return tag


async def update_tag(db: AsyncSession, tag: Tag, data: TagUpdate) -> Tag:
    if data.name is not None:
        tag.name = data.name
    if data.category_id is not None:
        tag.category_id = data.category_id
    await db.commit()
    await db.refresh(tag)
    return tag


async def delete_tag(db: AsyncSession, tag: Tag) -> None:
    await db.delete(tag)
    await db.commit()
