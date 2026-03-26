from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tag import Tag
from app.schemas.tag import TagCreate, TagUpdate


async def get_by_id(db: AsyncSession, tag_id: int) -> Optional[Tag]:
    result = await db.execute(select(Tag).where(Tag.id == tag_id))
    return result.scalar_one_or_none()


async def get_all(db: AsyncSession) -> List[Tag]:
    result = await db.execute(select(Tag))
    return list(result.scalars().all())


async def get_by_category(db: AsyncSession, category_id: int) -> List[Tag]:
    result = await db.execute(select(Tag).where(Tag.category_id == category_id))
    return list(result.scalars().all())


async def create(db: AsyncSession, data: TagCreate) -> Tag:
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


async def delete(db: AsyncSession, tag: Tag) -> None:
    await db.delete(tag)
    await db.commit()
