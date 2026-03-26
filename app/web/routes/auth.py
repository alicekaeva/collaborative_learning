from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse, HTMLResponse

from app.api.deps import DBDep
from app.crud import user as user_crud
from app.core.security import create_access_token
from app.schemas.user import UserCreate
from app.web.utils import templates, set_auth_cookie, clear_auth_cookie

router = APIRouter(tags=["web:auth"])


def _get_flash(request: Request) -> str | None:
    return request.cookies.get("flash_message")


def _clear_flash(response) -> None:
    response.delete_cookie("flash_message")


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    flash = _get_flash(request)
    response = templates.TemplateResponse(
        "auth/login.html",
        {"request": request, "user": None, "flash": flash},
    )
    if flash:
        _clear_flash(response)
    return response


@router.post("/login", response_class=HTMLResponse)
async def login_submit(
    request: Request,
    db: DBDep,
    email: str = Form(...),
    password: str = Form(...),
):
    user = await user_crud.get_by_email(db, email)
    if not user or not user_crud.authenticate(user, password):
        return templates.TemplateResponse(
            "auth/login.html",
            {
                "request": request,
                "user": None,
                "error": "Неверный email или пароль",
            },
            status_code=400,
        )
    token = create_access_token(subject=user.id, roles=user.roles)
    response = RedirectResponse(url="/", status_code=303)
    set_auth_cookie(response, token)
    return response


@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    flash = _get_flash(request)
    response = templates.TemplateResponse(
        "auth/register.html",
        {"request": request, "user": None, "flash": flash},
    )
    if flash:
        _clear_flash(response)
    return response


@router.post("/register", response_class=HTMLResponse)
async def register_submit(
    request: Request,
    db: DBDep,
    email: str = Form(...),
    full_name: str = Form(...),
    password: str = Form(...),
):
    existing = await user_crud.get_by_email(db, email)
    if existing:
        return templates.TemplateResponse(
            "auth/register.html",
            {
                "request": request,
                "user": None,
                "error": "Пользователь с таким email уже существует",
            },
            status_code=400,
        )
    user_data = UserCreate(email=email, full_name=full_name, password=password)
    user = await user_crud.create(db, user_data)
    token = create_access_token(subject=user.id, roles=user.roles)
    response = RedirectResponse(url="/", status_code=303)
    set_auth_cookie(response, token)
    return response


@router.get("/logout")
async def logout(request: Request):
    response = RedirectResponse(url="/login", status_code=303)
    clear_auth_cookie(response)
    return response
