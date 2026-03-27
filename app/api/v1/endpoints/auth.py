from fastapi import APIRouter, Request

from app.api.deps import AuthServiceDep, CurrentUser
from app.core.limiter import limiter
from app.schemas.auth import LoginRequest, RegisterRequest, RefreshRequest
from app.schemas.common import TokenPair, Message
from app.schemas.user import UserRead

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenPair, status_code=201)
@limiter.limit("10/minute")
async def register(request: Request, data: RegisterRequest, service: AuthServiceDep):
    return await service.register(data)


@router.post("/login", response_model=TokenPair)
@limiter.limit("20/minute")
async def login(request: Request, data: LoginRequest, service: AuthServiceDep):
    return await service.login(data)


@router.post("/refresh", response_model=TokenPair)
async def refresh_tokens(data: RefreshRequest, service: AuthServiceDep):
    return await service.refresh(data)


@router.post("/logout", response_model=Message)
async def logout(data: RefreshRequest, service: AuthServiceDep, current_user: CurrentUser):
    return await service.logout(data, current_user)


@router.get("/me", response_model=UserRead)
async def me(current_user: CurrentUser):
    return current_user
