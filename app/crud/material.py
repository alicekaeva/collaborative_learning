from typing import Optional, List
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.material import Material
from app.models.tag import Tag
from app.schemas.material import MaterialUpdate


async def get_by_id(db: AsyncSession, material_id: int) -> Optional[Material]:
    result = await db.execute(select(Material).where(Material.id == material_id))
    return result.scalar_one_or_none()


async def get_public(db: AsyncSession, skip: int = 0, limit: int = 50) -> List[Material]:
    result = await db.execute(
        select(Material).where(Material.is_private.is_(False)).offset(skip).limit(limit)
    )
    return list(result.scalars().all())


async def get_all(db: AsyncSession) -> List[Material]:
    result = await db.execute(select(Material))
    return list(result.scalars().all())


async def get_by_user(db: AsyncSession, user_id: int) -> List[Material]:
    result = await db.execute(
        select(Material).where(Material.creator_user_id == user_id)
    )
    return list(result.scalars().all())


async def get_by_group(db: AsyncSession, group_id: int) -> List[Material]:
    result = await db.execute(
        select(Material).where(Material.creator_group_id == group_id)
    )
    return list(result.scalars().all())


async def create(
    db: AsyncSession,
    name: str,
    file_link: str,
    mime_type: str,
    is_private: bool,
    creator_user_id: Optional[int] = None,
    creator_group_id: Optional[int] = None,
) -> Material:
    material = Material(
        name=name,
        file_link=file_link,
        mime_type=mime_type,
        is_private=is_private,
        creator_user_id=creator_user_id,
        creator_group_id=creator_group_id,
    )
    db.add(material)
    await db.commit()
    await db.refresh(material)
    return material


async def update_material(db: AsyncSession, material: Material, data: MaterialUpdate) -> Material:
    if data.name is not None:
        material.name = data.name
    if data.is_private is not None:
        material.is_private = data.is_private
    await db.commit()
    await db.refresh(material)
    return material


async def delete(db: AsyncSession, material: Material) -> None:
    await db.delete(material)
    await db.commit()
