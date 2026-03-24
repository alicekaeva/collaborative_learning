from typing import List, Optional

from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse, HTMLResponse

from app.api.deps import DBDep
from app.crud import user as user_crud
from app.schemas.user import UserUpdate
from app.web.deps import WebUser
from app.web.utils import templates, redirect

router = APIRouter(tags=["web:users"])


def _get_flash(request: Request) -> str | None:
    return request.cookies.get("flash_message")


def _clear_flash(response) -> None:
    response.delete_cookie("flash_message")


@router.get("/users/{user_id}", response_class=HTMLResponse)
async def user_profile(request: Request, user_id: int, db: DBDep, current_user: WebUser):
    profile_user = await user_crud.get_by_id(db, user_id)
    if not profile_user:
        return redirect("/", message="Пользователь не найден")

    flash = _get_flash(request)
    response = templates.TemplateResponse(
        "users/profile.html",
        {
            "request": request,
            "user": current_user,
            "profile_user": profile_user,
            "flash": flash,
        },
    )
    if flash:
        _clear_flash(response)
    return response


@router.get("/users/{user_id}/edit", response_class=HTMLResponse)
async def edit_user_form(request: Request, user_id: int, db: DBDep, current_user: WebUser):
    if not current_user:
        return RedirectResponse("/login", status_code=303)

    is_admin = "ROLE_ADMIN" in current_user.roles
    is_self = current_user.id == user_id
    if not is_self and not is_admin:
        return redirect(f"/users/{user_id}", message="Недостаточно прав")

    profile_user = await user_crud.get_by_id(db, user_id)
    if not profile_user:
        return redirect("/", message="Пользователь не найден")

    return templates.TemplateResponse(
        "users/edit.html",
        {"request": request, "user": current_user, "profile_user": profile_user},
    )


@router.post("/users/{user_id}/edit", response_class=HTMLResponse)
async def edit_user_submit(
    request: Request,
    user_id: int,
    db: DBDep,
    current_user: WebUser,
    email: Optional[str] = Form(default=None),
    full_name: Optional[str] = Form(default=None),
    phone_number: Optional[str] = Form(default=None),
    age: Optional[int] = Form(default=None),
    alma_mater: Optional[str] = Form(default=None),
    tag_ids: List[int] = Form(default=[]),
):
    if not current_user:
        return RedirectResponse("/login", status_code=303)

    is_admin = "ROLE_ADMIN" in current_user.roles
    is_self = current_user.id == user_id
    if not is_self and not is_admin:
        return redirect(f"/users/{user_id}", message="Недостаточно прав")

    profile_user = await user_crud.get_by_id(db, user_id)
    if not profile_user:
        return redirect("/", message="Пользователь не найден")

    data = UserUpdate(
        email=email or None,
        full_name=full_name or None,
        phone_number=phone_number or None,
        age=age,
        alma_mater=alma_mater or None,
        tag_ids=tag_ids if tag_ids else None,
    )
    await user_crud.update_user(db, profile_user, data)
    return redirect(f"/users/{user_id}", message="Профиль обновлён")


@router.post("/users/earn-points", response_class=HTMLResponse)
async def earn_points(
    request: Request,
    db: DBDep,
    current_user: WebUser,
    student_user_id: int = Form(...),
    points: int = Form(...),
):
    if not current_user:
        return RedirectResponse("/login", status_code=303)

    is_teacher = "ROLE_TEACHER" in current_user.roles
    is_admin = "ROLE_ADMIN" in current_user.roles
    if not is_teacher and not is_admin:
        return redirect("/", message="Только преподаватели могут начислять баллы")

    student_user = await user_crud.get_by_id(db, student_user_id)
    if not student_user:
        return redirect("/", message="Студент не найден")

    await user_crud.earn_points(db, student_user, points)
    return redirect(f"/users/{student_user_id}", message=f"Начислено {points} баллов")
