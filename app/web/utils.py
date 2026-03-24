from fastapi import Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path

templates = Jinja2Templates(directory=str(Path(__file__).parent.parent.parent / "templates"))


def redirect(url: str, message: str = None) -> RedirectResponse:
    response = RedirectResponse(url=url, status_code=303)
    if message:
        response.set_cookie("flash_message", message, max_age=5)
    return response


def set_auth_cookie(response, token: str) -> None:
    response.set_cookie("access_token", token, httponly=True, samesite="lax", max_age=1800)


def clear_auth_cookie(response) -> None:
    response.delete_cookie("access_token")
