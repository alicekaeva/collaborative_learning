from __future__ import annotations

from typing import Annotated
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_token
from app.core.exceptions import UnauthorizedError, ForbiddenError
from app.db.session import get_db
from app.modules.identity.models.user import User
from app.modules.identity.models.student import Student
from app.modules.identity.models.teacher import Teacher
from app.modules.identity.service import AuthService
from app.modules.groups.service import GroupService

bearer_scheme = HTTPBearer(auto_error=False)

DBDep = Annotated[AsyncSession, Depends(get_db)]


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    db: DBDep,
) -> User:
    if not credentials:
        raise UnauthorizedError("Необходима авторизация")
    payload = decode_token(credentials.credentials)
    if not payload or payload.get("type") != "access":
        raise UnauthorizedError("Недействительный токен")
    user_id = int(payload["sub"])
    result = await db.execute(
        select(User)
        .where(User.id == user_id)
        .options(
            selectinload(User.tags),
            selectinload(User.student_profile).selectinload(Student.groups),
            selectinload(User.teacher_profile).selectinload(Teacher.groups),
            selectinload(User.admin_profile),
        )
    )
    user = result.scalar_one_or_none()
    if not user:
        raise UnauthorizedError("Пользователь не найден")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def require_roles(*roles: str):
    async def checker(current_user: CurrentUser) -> User:
        if not any(r in current_user.roles for r in roles):
            raise ForbiddenError("Недостаточно прав")
        return current_user
    return checker


# ------------------------------------------------------------------ service deps

def _get_auth_service(db: DBDep) -> AuthService:
    return AuthService(db)


def _get_group_service(db: DBDep) -> GroupService:
    return GroupService(db)


AuthServiceDep = Annotated[AuthService, Depends(_get_auth_service)]
GroupServiceDep = Annotated[GroupService, Depends(_get_group_service)]
