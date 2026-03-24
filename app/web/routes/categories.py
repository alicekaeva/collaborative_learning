from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse, HTMLResponse

from app.api.deps import DBDep
from app.crud import category as category_crud
from app.schemas.category import CategoryCreate, CategoryUpdate
from app.web.deps import WebUser
from app.web.utils import templates, redirect

router = APIRouter(tags=["web:categories"])


def _get_flash(request: Request) -> str | None:
    return request.cookies.get("flash_message")


def _clear_flash(response) -> None:
    response.delete_cookie("flash_message")


@router.get("/categories", response_class=HTMLResponse)
async def category_list(request: Request, db: DBDep, current_user: WebUser):
    if not current_user:
        return RedirectResponse("/login", status_code=303)
    if "ROLE_ADMIN" not in current_user.roles:
        return redirect("/", message="Недостаточно прав")

    categories = await category_crud.get_all(db)

    flash = _get_flash(request)
    response = templates.TemplateResponse(
        "categories/list.html",
        {
            "request": request,
            "user": current_user,
            "categories": categories,
            "flash": flash,
        },
    )
    if flash:
        _clear_flash(response)
    return response


@router.get("/categories/new", response_class=HTMLResponse)
async def new_category_form(request: Request, current_user: WebUser):
    if not current_user:
        return RedirectResponse("/login", status_code=303)
    if "ROLE_ADMIN" not in current_user.roles:
        return redirect("/", message="Недостаточно прав")

    return templates.TemplateResponse(
        "categories/new.html",
        {"request": request, "user": current_user},
    )


@router.post("/categories/new", response_class=HTMLResponse)
async def new_category_submit(
    request: Request,
    db: DBDep,
    current_user: WebUser,
    name: str = Form(...),
):
    if not current_user:
        return RedirectResponse("/login", status_code=303)
    if "ROLE_ADMIN" not in current_user.roles:
        return redirect("/", message="Недостаточно прав")

    data = CategoryCreate(name=name)
    await category_crud.create(db, data)
    return redirect("/categories", message="Категория успешно создана")


@router.get("/categories/{category_id}/edit", response_class=HTMLResponse)
async def edit_category_form(request: Request, category_id: int, db: DBDep, current_user: WebUser):
    if not current_user:
        return RedirectResponse("/login", status_code=303)
    if "ROLE_ADMIN" not in current_user.roles:
        return redirect("/", message="Недостаточно прав")

    category = await category_crud.get_by_id(db, category_id)
    if not category:
        return redirect("/categories", message="Категория не найдена")

    return templates.TemplateResponse(
        "categories/edit.html",
        {"request": request, "user": current_user, "category": category},
    )


@router.post("/categories/{category_id}/edit", response_class=HTMLResponse)
async def edit_category_submit(
    request: Request,
    category_id: int,
    db: DBDep,
    current_user: WebUser,
    name: str = Form(...),
):
    if not current_user:
        return RedirectResponse("/login", status_code=303)
    if "ROLE_ADMIN" not in current_user.roles:
        return redirect("/", message="Недостаточно прав")

    category = await category_crud.get_by_id(db, category_id)
    if not category:
        return redirect("/categories", message="Категория не найдена")

    data = CategoryUpdate(name=name)
    await category_crud.update_category(db, category, data)
    return redirect("/categories", message="Категория обновлена")


@router.post("/categories/{category_id}/delete", response_class=HTMLResponse)
async def delete_category(request: Request, category_id: int, db: DBDep, current_user: WebUser):
    if not current_user:
        return RedirectResponse("/login", status_code=303)
    if "ROLE_ADMIN" not in current_user.roles:
        return redirect("/", message="Недостаточно прав")

    category = await category_crud.get_by_id(db, category_id)
    if not category:
        return redirect("/categories", message="Категория не найдена")

    await category_crud.delete(db, category)
    return redirect("/categories", message="Категория удалена")
