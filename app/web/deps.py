from typing import Optional, Annotated
from fastapi import Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.core.security import decode_token
from app.models.user import User
from app.crud import user as user_crud


async def get_current_user_optional(request: Request, db: AsyncSession = Depends(get_db)) -> Optional[User]:
    token = request.cookies.get("access_token")
    if not token:
        return None
    payload = decode_token(token)
    if not payload or payload.get("type") != "access":
        return None
    user = await user_crud.get_by_id(db, int(payload["sub"]))
    return user


async def get_current_user_required(request: Request, db: AsyncSession = Depends(get_db)) -> User:
    user = await get_current_user_optional(request, db)
    if not user:
        from fastapi.responses import RedirectResponse
        # We can't redirect from a Depends easily, so raise and handle in route
        raise Exception("redirect:/login")
    return user


WebUser = Annotated[Optional[User], Depends(get_current_user_optional)]
WebUserRequired = Annotated[User, Depends(get_current_user_required)]
