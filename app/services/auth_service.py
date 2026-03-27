from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, create_refresh_token
from app.core.exceptions import ConflictError, UnauthorizedError, ForbiddenError
from app.crud import user as user_crud
from app.schemas.auth import LoginRequest, RegisterRequest, RefreshRequest
from app.schemas.common import TokenPair, Message
from app.schemas.user import UserCreate
from app.services.cache import store_refresh_token, validate_refresh_token, revoke_refresh_token
from app.models.user import User


class AuthService:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def register(self, data: RegisterRequest) -> TokenPair:
        if await user_crud.get_by_email(self._db, data.email):
            raise ConflictError("Пользователь с таким email уже существует")
        user = await user_crud.create(self._db, UserCreate(**data.model_dump()))
        return await self._issue_tokens(user)

    async def login(self, data: LoginRequest) -> TokenPair:
        user = await user_crud.get_by_email(self._db, data.email)
        if not user or not user_crud.authenticate(user, data.password):
            raise UnauthorizedError("Неверный email или пароль")
        return await self._issue_tokens(user)

    async def refresh(self, data: RefreshRequest) -> TokenPair:
        user_id = await validate_refresh_token(data.refresh_token)
        if not user_id:
            raise UnauthorizedError("Недействительный refresh токен")
        user = await user_crud.get_by_id(self._db, user_id)
        if not user:
            raise UnauthorizedError("Пользователь не найден")
        await revoke_refresh_token(data.refresh_token)
        return await self._issue_tokens(user)

    async def logout(self, data: RefreshRequest, current_user: User) -> Message:
        token_owner_id = await validate_refresh_token(data.refresh_token)
        if token_owner_id != current_user.id:
            raise ForbiddenError("Токен не принадлежит текущему пользователю")
        await revoke_refresh_token(data.refresh_token)
        return Message(detail="Выход выполнен успешно")

    async def _issue_tokens(self, user: User) -> TokenPair:
        access = create_access_token(user.id, user.roles)
        refresh = create_refresh_token(user.id)
        await store_refresh_token(user.id, refresh)
        return TokenPair(access_token=access, refresh_token=refresh)
