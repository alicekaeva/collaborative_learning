from typing import List, Optional
from fastapi import APIRouter

from app.api.deps import DBDep, CurrentUser
from app.core.exceptions import NotFoundError, ForbiddenError
from app.crud import post as post_crud
from app.schemas.post import PostCreate, PostUpdate, PostRead
from app.schemas.common import Message
from app.services.cache import get_cached, set_cached

router = APIRouter(prefix="/posts", tags=["posts"])


@router.get("/", response_model=List[PostRead])
async def list_posts(
    db: DBDep,
    tag_id: Optional[int] = None,
    category_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 50,
):
    if tag_id:
        return await post_crud.get_by_tag(db, tag_id)
    if category_id:
        return await post_crud.get_by_category(db, category_id)
    return await post_crud.get_all(db, skip=skip, limit=limit)


@router.get("/recommended", response_model=List[PostRead])
async def recommended_posts(db: DBDep, current_user: CurrentUser):
    cache_key = f"posts:recommended:{current_user.id}"
    cached = await get_cached(cache_key)
    if cached:
        return cached

    tag_ids = [t.id for t in current_user.tags]
    posts = await post_crud.get_recommended(db, tag_ids)
    result = [PostRead.model_validate(p) for p in posts]
    data = [r.model_dump(mode="json") for r in result]
    await set_cached(cache_key, data)
    return result


@router.get("/favorites", response_model=List[PostRead])
async def favorite_posts(db: DBDep, current_user: CurrentUser):
    return await post_crud.get_favorites(db, current_user.id)


@router.get("/user/{user_id}", response_model=List[PostRead])
async def user_posts(user_id: int, db: DBDep):
    return await post_crud.get_by_author(db, user_id)


@router.post("/", response_model=PostRead, status_code=201)
async def create_post(data: PostCreate, db: DBDep, current_user: CurrentUser):
    return await post_crud.create(db, data, current_user.id)


@router.get("/{post_id}", response_model=PostRead)
async def get_post(post_id: int, db: DBDep):
    post = await post_crud.get_by_id(db, post_id)
    if not post:
        raise NotFoundError("Пост не найден")
    return post


@router.patch("/{post_id}", response_model=PostRead)
async def update_post(post_id: int, data: PostUpdate, db: DBDep, current_user: CurrentUser):
    post = await post_crud.get_by_id(db, post_id)
    if not post:
        raise NotFoundError("Пост не найден")
    if post.author_id != current_user.id and "ROLE_ADMIN" not in current_user.roles:
        raise ForbiddenError("Нет доступа для редактирования этого поста")
    return await post_crud.update_post(db, post, data)


@router.delete("/{post_id}", response_model=Message)
async def delete_post(post_id: int, db: DBDep, current_user: CurrentUser):
    post = await post_crud.get_by_id(db, post_id)
    if not post:
        raise NotFoundError("Пост не найден")
    if post.author_id != current_user.id and "ROLE_ADMIN" not in current_user.roles:
        raise ForbiddenError("Нет доступа для удаления этого поста")
    await post_crud.delete(db, post)
    return Message(detail="Пост удалён")


@router.post("/{post_id}/favorite", response_model=Message)
async def add_to_favorites(post_id: int, db: DBDep, current_user: CurrentUser):
    post = await post_crud.get_by_id(db, post_id)
    if not post:
        raise NotFoundError("Пост не найден")
    await post_crud.add_to_favorites(db, post, current_user)
    return Message(detail="Пост добавлен в избранное")


@router.delete("/{post_id}/favorite", response_model=Message)
async def remove_from_favorites(post_id: int, db: DBDep, current_user: CurrentUser):
    post = await post_crud.get_by_id(db, post_id)
    if not post:
        raise NotFoundError("Пост не найден")
    await post_crud.remove_from_favorites(db, post, current_user)
    return Message(detail="Пост удалён из избранного")
