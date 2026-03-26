from fastapi import APIRouter, Request

from app.api.deps import DBDep, CurrentUser
from app.core.limiter import limiter
from app.core.security import create_access_token, create_refresh_token
from app.core.exceptions import ConflictError, UnauthorizedError, ForbiddenError
from app.crud import user as user_crud
from app.schemas.auth import LoginRequest, RegisterRequest, RefreshRequest
from app.schemas.common import TokenPair, Message
from app.schemas.user import UserRead, UserCreate
from app.services.cache import store_refresh_token, validate_refresh_token, revoke_refresh_token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenPair, status_code=201)
@limiter.limit("10/minute")
async def register(request: Request, data: RegisterRequest, db: DBDep):
    if await user_crud.get_by_email(db, data.email):
        raise ConflictError("Пользователь с таким email уже существует")
    user = await user_crud.create(db, UserCreate(**data.model_dump()))
    access = create_access_token(user.id, user.roles)
    refresh = create_refresh_token(user.id)
    await store_refresh_token(user.id, refresh)
    return TokenPair(access_token=access, refresh_token=refresh)


@router.post("/login", response_model=TokenPair)
@limiter.limit("20/minute")
async def login(request: Request, data: LoginRequest, db: DBDep):
    user = await user_crud.get_by_email(db, data.email)
    if not user or not user_crud.authenticate(user, data.password):
        raise UnauthorizedError("Неверный email или пароль")
    access = create_access_token(user.id, user.roles)
    refresh = create_refresh_token(user.id)
    await store_refresh_token(user.id, refresh)
    return TokenPair(access_token=access, refresh_token=refresh)


@router.post("/refresh", response_model=TokenPair)
async def refresh_tokens(data: RefreshRequest, db: DBDep):
    user_id = await validate_refresh_token(data.refresh_token)
    if not user_id:
        raise UnauthorizedError("Недействительный refresh токен")
    user = await user_crud.get_by_id(db, user_id)
    if not user:
        raise UnauthorizedError("Пользователь не найден")
    await revoke_refresh_token(data.refresh_token)
    access = create_access_token(user.id, user.roles)
    new_refresh = create_refresh_token(user.id)
    await store_refresh_token(user.id, new_refresh)
    return TokenPair(access_token=access, refresh_token=new_refresh)


@router.post("/logout", response_model=Message)
async def logout(data: RefreshRequest, current_user: CurrentUser):
    token_owner_id = await validate_refresh_token(data.refresh_token)
    if token_owner_id != current_user.id:
        raise ForbiddenError("Токен не принадлежит текущему пользователю")
    await revoke_refresh_token(data.refresh_token)
    return Message(detail="Выход выполнен успешно")


@router.get("/me", response_model=UserRead)
async def me(current_user: CurrentUser):
    return current_user
