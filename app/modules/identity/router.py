from typing import List, Annotated
from fastapi import APIRouter, Depends, Request

from app.api.deps import DBDep, CurrentUser, require_roles
from app.modules.identity.models.user import User
from app.modules.identity.service import AuthService
from app.core.exceptions import NotFoundError, ForbiddenError
from app.core.limiter import limiter
from app.modules.identity import repository as user_repo
from app.modules.identity.schemas.auth import LoginRequest, RegisterRequest, RefreshRequest
from app.modules.identity.schemas.user import UserRead, UserUpdate, EarnPointsRequest
from app.schemas.common import TokenPair, Message

auth_router = APIRouter(prefix="/auth", tags=["auth"])
users_router = APIRouter(prefix="/users", tags=["users"])


def _get_auth_service(db: DBDep) -> AuthService:
    return AuthService(db)


AuthServiceDep = Annotated[AuthService, Depends(_get_auth_service)]


# ------------------------------------------------------------------ Auth

@auth_router.post("/register", response_model=TokenPair, status_code=201)
@limiter.limit("10/minute")
async def register(request: Request, data: RegisterRequest, service: AuthServiceDep):
    return await service.register(data)


@auth_router.post("/login", response_model=TokenPair)
@limiter.limit("20/minute")
async def login(request: Request, data: LoginRequest, service: AuthServiceDep):
    return await service.login(data)


@auth_router.post("/refresh", response_model=TokenPair)
async def refresh_tokens(data: RefreshRequest, service: AuthServiceDep):
    return await service.refresh(data)


@auth_router.post("/logout", response_model=Message)
async def logout(data: RefreshRequest, service: AuthServiceDep, current_user: CurrentUser):
    return await service.logout(data, current_user)


@auth_router.get("/me", response_model=UserRead)
async def me(current_user: CurrentUser):
    return current_user


# ------------------------------------------------------------------ Users

@users_router.get("/", response_model=List[UserRead])
async def list_users(db: DBDep, current_user: CurrentUser, skip: int = 0, limit: int = 100):
    return await user_repo.get_all(db, skip=skip, limit=limit)


@users_router.get("/{user_id}", response_model=UserRead)
async def get_user(user_id: int, db: DBDep, current_user: CurrentUser):
    user = await user_repo.get_by_id(db, user_id)
    if not user:
        raise NotFoundError("Пользователь не найден")
    return user


@users_router.patch("/{user_id}", response_model=UserRead)
async def update_user(user_id: int, data: UserUpdate, db: DBDep, current_user: CurrentUser):
    if current_user.id != user_id and "ROLE_ADMIN" not in current_user.roles:
        raise ForbiddenError("Нет доступа для редактирования этого пользователя")
    user = await user_repo.get_by_id(db, user_id)
    if not user:
        raise NotFoundError("Пользователь не найден")
    return await user_repo.update_user(db, user, data)


@users_router.delete("/{user_id}", status_code=204)
async def delete_user(user_id: int, db: DBDep, current_user: CurrentUser):
    if current_user.id != user_id and "ROLE_ADMIN" not in current_user.roles:
        raise ForbiddenError("Нет доступа для удаления этого пользователя")
    user = await user_repo.get_by_id(db, user_id)
    if not user:
        raise NotFoundError("Пользователь не найден")
    await user_repo.delete(db, user)


@users_router.post("/{user_id}/points", response_model=UserRead)
async def earn_points(
    user_id: int,
    data: EarnPointsRequest,
    db: DBDep,
    _: User = Depends(require_roles("ROLE_TEACHER")),
):
    user = await user_repo.get_by_id(db, user_id)
    if not user:
        raise NotFoundError("Студент не найден")
    if "ROLE_STUDENT" not in user.roles:
        raise ForbiddenError("Пользователь не является студентом")
    return await user_repo.earn_points(db, user, data.points)
