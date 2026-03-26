from typing import Optional
from pathlib import Path

from fastapi.responses import RedirectResponse, Response
from fastapi.templating import Jinja2Templates

from app.core.config import settings

templates = Jinja2Templates(directory=str(Path(__file__).parent.parent.parent / "templates"))


def redirect(url: str, message: Optional[str] = None) -> RedirectResponse:
    response = RedirectResponse(url=url, status_code=303)
    if message:
        response.set_cookie("flash_message", message, max_age=5, httponly=True)
    return response


def set_auth_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        "access_token",
        token,
        httponly=True,
        samesite="lax",
        max_age=1800,
        secure=settings.COOKIE_SECURE,
    )


def clear_auth_cookie(response: Response) -> None:
    response.delete_cookie("access_token")
