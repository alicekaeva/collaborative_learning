from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.identity.models.user import User
from app.modules.taxonomy.models.tag import Tag
from app.core.security import get_password_hash, verify_password
from app.modules.identity.schemas.user import UserCreate, UserUpdate


async def get_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def get_by_email(db: AsyncSession, email: str) -> Optional[User]:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def get_all(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[User]:
    result = await db.execute(select(User).offset(skip).limit(limit))
    return list(result.scalars().all())


async def create(db: AsyncSession, data: UserCreate) -> User:
    user = User(
        email=data.email,
        full_name=data.full_name,
        password_hash=get_password_hash(data.password),
        roles=["ROLE_USER"],
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def update_user(db: AsyncSession, user: User, data: UserUpdate) -> User:
    if data.email is not None:
        user.email = data.email
    if data.full_name is not None:
        user.full_name = data.full_name
    if data.phone_number is not None:
        user.phone_number = data.phone_number
    if data.age is not None:
        user.age = data.age
    if data.alma_mater is not None:
        user.alma_mater = data.alma_mater
    if data.tag_ids is not None:
        tags_result = await db.execute(select(Tag).where(Tag.id.in_(data.tag_ids)))
        user.tags = list(tags_result.scalars().all())
    await db.commit()
    await db.refresh(user)
    return user


async def delete(db: AsyncSession, user: User) -> None:
    await db.delete(user)
    await db.commit()


async def add_role(db: AsyncSession, user: User, role: str) -> User:
    if role not in user.roles:
        user.roles = user.roles + [role]
        await db.commit()
        await db.refresh(user)
    return user


async def remove_role(db: AsyncSession, user: User, role: str) -> User:
    user.roles = [r for r in user.roles if r != role]
    await db.commit()
    await db.refresh(user)
    return user


async def earn_points(db: AsyncSession, user: User, points: int) -> User:
    user.points_amount += points
    await db.commit()
    await db.refresh(user)
    return user


def authenticate(user: User, password: str) -> bool:
    return verify_password(password, user.password_hash)
