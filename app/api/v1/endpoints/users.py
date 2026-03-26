from typing import List
from fastapi import APIRouter, Depends

from app.api.deps import DBDep, CurrentUser, require_roles
from app.models.user import User
from app.core.exceptions import NotFoundError, ForbiddenError
from app.crud import user as user_crud
from app.schemas.user import UserRead, UserUpdate, EarnPointsRequest

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=List[UserRead])
async def list_users(db: DBDep, current_user: CurrentUser, skip: int = 0, limit: int = 100):
    return await user_crud.get_all(db, skip=skip, limit=limit)


@router.get("/{user_id}", response_model=UserRead)
async def get_user(user_id: int, db: DBDep, current_user: CurrentUser):
    user = await user_crud.get_by_id(db, user_id)
    if not user:
        raise NotFoundError("Пользователь не найден")
    return user


@router.patch("/{user_id}", response_model=UserRead)
async def update_user(user_id: int, data: UserUpdate, db: DBDep, current_user: CurrentUser):
    if current_user.id != user_id and "ROLE_ADMIN" not in current_user.roles:
        raise ForbiddenError("Нет доступа для редактирования этого пользователя")
    user = await user_crud.get_by_id(db, user_id)
    if not user:
        raise NotFoundError("Пользователь не найден")
    return await user_crud.update_user(db, user, data)


@router.delete("/{user_id}", status_code=204)
async def delete_user(user_id: int, db: DBDep, current_user: CurrentUser):
    if current_user.id != user_id and "ROLE_ADMIN" not in current_user.roles:
        raise ForbiddenError("Нет доступа для удаления этого пользователя")
    user = await user_crud.get_by_id(db, user_id)
    if not user:
        raise NotFoundError("Пользователь не найден")
    await user_crud.delete(db, user)


@router.post("/{user_id}/points", response_model=UserRead)
async def earn_points(
    user_id: int,
    data: EarnPointsRequest,
    db: DBDep,
    _: User = Depends(require_roles("ROLE_TEACHER")),
):
    user = await user_crud.get_by_id(db, user_id)
    if not user:
        raise NotFoundError("Студент не найден")
    if "ROLE_STUDENT" not in user.roles:
        raise ForbiddenError("Пользователь не является студентом")
    return await user_crud.earn_points(db, user, data.points)
