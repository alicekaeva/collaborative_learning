from typing import Optional, List
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.content.models.post import Post
from app.modules.taxonomy.models.tag import Tag
from app.modules.identity.models.user import User
from app.modules.content.schemas.post import PostCreate, PostUpdate


async def get_by_id(db: AsyncSession, post_id: int) -> Optional[Post]:
    result = await db.execute(select(Post).where(Post.id == post_id))
    return result.scalar_one_or_none()


async def get_all(db: AsyncSession, skip: int = 0, limit: int = 50) -> List[Post]:
    result = await db.execute(
        select(Post).order_by(desc(Post.posting_date)).offset(skip).limit(limit)
    )
    return list(result.scalars().all())


async def get_by_author(db: AsyncSession, author_id: int) -> List[Post]:
    result = await db.execute(
        select(Post).where(Post.author_id == author_id).order_by(desc(Post.posting_date))
    )
    return list(result.scalars().all())


async def get_by_tag(
    db: AsyncSession, tag_id: int, skip: int = 0, limit: int = 50
) -> List[Post]:
    result = await db.execute(
        select(Post)
        .where(Post.tags.any(Tag.id == tag_id))
        .distinct()
        .order_by(desc(Post.posting_date))
        .offset(skip)
        .limit(limit)
    )
    return list(result.scalars().all())


async def get_by_category(
    db: AsyncSession, category_id: int, skip: int = 0, limit: int = 50
) -> List[Post]:
    result = await db.execute(
        select(Post)
        .where(Post.tags.any(Tag.category_id == category_id))
        .distinct()
        .order_by(desc(Post.posting_date))
        .offset(skip)
        .limit(limit)
    )
    return list(result.scalars().all())


async def get_recommended(db: AsyncSession, tag_ids: List[int]) -> List[Post]:
    if not tag_ids:
        return []
    result = await db.execute(
        select(Post)
        .where(Post.tags.any(Tag.id.in_(tag_ids)))
        .distinct()
        .order_by(desc(Post.posting_date))
        .limit(50)
    )
    return list(result.scalars().all())


async def get_favorites(db: AsyncSession, user_id: int) -> List[Post]:
    result = await db.execute(
        select(Post)
        .where(Post.favorited_by.any(User.id == user_id))
        .order_by(desc(Post.posting_date))
    )
    return list(result.scalars().all())


async def create(db: AsyncSession, data: PostCreate, author_id: int) -> Post:
    tags_result = await db.execute(select(Tag).where(Tag.id.in_(data.tag_ids)))
    tags = list(tags_result.scalars().all())
    post = Post(content=data.content, author_id=author_id, tags=tags)
    db.add(post)
    await db.commit()
    await db.refresh(post)
    return post


async def update_post(db: AsyncSession, post: Post, data: PostUpdate) -> Post:
    if data.content is not None:
        post.content = data.content
    if data.tag_ids is not None:
        tags_result = await db.execute(select(Tag).where(Tag.id.in_(data.tag_ids)))
        post.tags = list(tags_result.scalars().all())
    await db.commit()
    await db.refresh(post)
    return post


async def delete(db: AsyncSession, post: Post) -> None:
    await db.delete(post)
    await db.commit()


async def add_to_favorites(db: AsyncSession, post: Post, user: User) -> None:
    result = await db.execute(
        select(Post).where(Post.id == post.id).options(selectinload(Post.favorited_by))
    )
    post = result.scalar_one()
    if user not in post.favorited_by:
        post.favorited_by.append(user)
        await db.commit()


async def remove_from_favorites(db: AsyncSession, post: Post, user: User) -> None:
    result = await db.execute(
        select(Post).where(Post.id == post.id).options(selectinload(Post.favorited_by))
    )
    post = result.scalar_one()
    post.favorited_by = [u for u in post.favorited_by if u.id != user.id]
    await db.commit()
