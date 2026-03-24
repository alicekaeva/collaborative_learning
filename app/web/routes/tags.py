from typing import Optional

from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse, HTMLResponse

from app.api.deps import DBDep
from app.crud import tag as tag_crud, category as category_crud
from app.schemas.tag import TagCreate, TagUpdate
from app.web.deps import WebUser
from app.web.utils import templates, redirect

router = APIRouter(tags=["web:tags"])


def _get_flash(request: Request) -> str | None:
    return request.cookies.get("flash_message")


def _clear_flash(response) -> None:
    response.delete_cookie("flash_message")


@router.get("/tags", response_class=HTMLResponse)
async def tag_list(request: Request, db: DBDep, current_user: WebUser):
    if not current_user:
        return RedirectResponse("/login", status_code=303)
    if "ROLE_ADMIN" not in current_user.roles:
        return redirect("/", message="Недостаточно прав")

    tags = await tag_crud.get_all(db)
    all_categories = await category_crud.get_all(db)

    flash = _get_flash(request)
    response = templates.TemplateResponse(
        "tags/list.html",
        {
            "request": request,
            "user": current_user,
            "tags": tags,
            "categories": all_categories,
            "flash": flash,
        },
    )
    if flash:
        _clear_flash(response)
    return response


@router.get("/tags/new", response_class=HTMLResponse)
async def new_tag_form(request: Request, db: DBDep, current_user: WebUser):
    if not current_user:
        return RedirectResponse("/login", status_code=303)
    if "ROLE_ADMIN" not in current_user.roles:
        return redirect("/", message="Недостаточно прав")

    all_categories = await category_crud.get_all(db)
    return templates.TemplateResponse(
        "tags/new.html",
        {"request": request, "user": current_user, "categories": all_categories},
    )


@router.post("/tags/new", response_class=HTMLResponse)
async def new_tag_submit(
    request: Request,
    db: DBDep,
    current_user: WebUser,
    name: str = Form(...),
    category_id: Optional[int] = Form(default=None),
):
    if not current_user:
        return RedirectResponse("/login", status_code=303)
    if "ROLE_ADMIN" not in current_user.roles:
        return redirect("/", message="Недостаточно прав")

    data = TagCreate(name=name, category_id=category_id)
    await tag_crud.create(db, data)
    return redirect("/tags", message="Тег успешно создан")


@router.get("/tags/{tag_id}/edit", response_class=HTMLResponse)
async def edit_tag_form(request: Request, tag_id: int, db: DBDep, current_user: WebUser):
    if not current_user:
        return RedirectResponse("/login", status_code=303)
    if "ROLE_ADMIN" not in current_user.roles:
        return redirect("/", message="Недостаточно прав")

    tag = await tag_crud.get_by_id(db, tag_id)
    if not tag:
        return redirect("/tags", message="Тег не найден")

    all_categories = await category_crud.get_all(db)
    return templates.TemplateResponse(
        "tags/edit.html",
        {"request": request, "user": current_user, "tag": tag, "categories": all_categories},
    )


@router.post("/tags/{tag_id}/edit", response_class=HTMLResponse)
async def edit_tag_submit(
    request: Request,
    tag_id: int,
    db: DBDep,
    current_user: WebUser,
    name: str = Form(...),
    category_id: Optional[int] = Form(default=None),
):
    if not current_user:
        return RedirectResponse("/login", status_code=303)
    if "ROLE_ADMIN" not in current_user.roles:
        return redirect("/", message="Недостаточно прав")

    tag = await tag_crud.get_by_id(db, tag_id)
    if not tag:
        return redirect("/tags", message="Тег не найден")

    data = TagUpdate(name=name, category_id=category_id)
    await tag_crud.update_tag(db, tag, data)
    return redirect("/tags", message="Тег обновлён")


@router.post("/tags/{tag_id}/delete", response_class=HTMLResponse)
async def delete_tag(request: Request, tag_id: int, db: DBDep, current_user: WebUser):
    if not current_user:
        return RedirectResponse("/login", status_code=303)
    if "ROLE_ADMIN" not in current_user.roles:
        return redirect("/", message="Недостаточно прав")

    tag = await tag_crud.get_by_id(db, tag_id)
    if not tag:
        return redirect("/tags", message="Тег не найден")

    await tag_crud.delete(db, tag)
    return redirect("/tags", message="Тег удалён")
