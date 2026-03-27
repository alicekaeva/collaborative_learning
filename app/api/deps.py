from typing import Annotated
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_token
from app.core.exceptions import UnauthorizedError, ForbiddenError
from app.db.session import get_db
from app.models.user import User
from app.models.student import Student
from app.models.teacher import Teacher

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

def _get_auth_service(db: DBDep) -> "AuthService":
    from app.services.auth_service import AuthService
    return AuthService(db)


def _get_group_service(db: DBDep) -> "GroupService":
    from app.services.group_service import GroupService
    return GroupService(db)


from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.services.auth_service import AuthService
    from app.services.group_service import GroupService

AuthServiceDep = Annotated["AuthService", Depends(_get_auth_service)]
GroupServiceDep = Annotated["GroupService", Depends(_get_group_service)]
