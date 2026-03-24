from typing import Annotated
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_token
from app.core.exceptions import UnauthorizedError, ForbiddenError
from app.db.session import get_db
from app.models.user import User
from app.crud import user as user_crud

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
    user = await user_crud.get_by_id(db, user_id)
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
