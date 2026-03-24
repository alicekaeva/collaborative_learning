from typing import Optional, List

from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse, HTMLResponse

from app.api.deps import DBDep
from app.crud import post as post_crud, tag as tag_crud, category as category_crud
from app.schemas.post import PostCreate, PostUpdate
from app.web.deps import WebUser
from app.web.utils import templates, redirect

router = APIRouter(tags=["web:posts"])


def _get_flash(request: Request) -> str | None:
    return request.cookies.get("flash_message")


def _clear_flash(response) -> None:
    response.delete_cookie("flash_message")


@router.get("/", response_class=HTMLResponse)
async def post_list(
    request: Request,
    db: DBDep,
    current_user: WebUser,
    tag_id: Optional[int] = None,
    category_id: Optional[int] = None,
):
    if tag_id:
        posts = await post_crud.get_by_tag(db, tag_id)
    elif category_id:
        posts = await post_crud.get_by_category(db, category_id)
    else:
        posts = await post_crud.get_all(db)

    all_tags = await tag_crud.get_all(db)
    all_categories = await category_crud.get_all(db)

    flash = _get_flash(request)
    response = templates.TemplateResponse(
        "posts/list.html",
        {
            "request": request,
            "user": current_user,
            "posts": posts,
            "tags": all_tags,
            "categories": all_categories,
            "selected_tag_id": tag_id,
            "selected_category_id": category_id,
            "flash": flash,
        },
    )
    if flash:
        _clear_flash(response)
    return response


@router.get("/posts/recommended", response_class=HTMLResponse)
async def posts_recommended(request: Request, db: DBDep, current_user: WebUser):
    if not current_user:
        return RedirectResponse("/login", status_code=303)
    tag_ids = [t.id for t in current_user.tags]
    posts = await post_crud.get_recommended(db, tag_ids)
    return templates.TemplateResponse(
        "posts/recommended.html",
        {"request": request, "user": current_user, "posts": posts},
    )


@router.get("/posts/my", response_class=HTMLResponse)
async def my_posts(request: Request, db: DBDep, current_user: WebUser):
    if not current_user:
        return RedirectResponse("/login", status_code=303)
    posts = await post_crud.get_by_author(db, current_user.id)
    return templates.TemplateResponse(
        "posts/my.html",
        {"request": request, "user": current_user, "posts": posts},
    )


@router.get("/posts/favorites", response_class=HTMLResponse)
async def post_favorites(request: Request, db: DBDep, current_user: WebUser):
    if not current_user:
        return RedirectResponse("/login", status_code=303)
    posts = await post_crud.get_favorites(db, current_user.id)
    return templates.TemplateResponse(
        "posts/favorites.html",
        {"request": request, "user": current_user, "posts": posts},
    )


@router.get("/posts/new", response_class=HTMLResponse)
async def new_post_form(request: Request, db: DBDep, current_user: WebUser):
    if not current_user:
        return RedirectResponse("/login", status_code=303)
    all_tags = await tag_crud.get_all(db)
    return templates.TemplateResponse(
        "posts/new.html",
        {"request": request, "user": current_user, "tags": all_tags},
    )


@router.post("/posts/new", response_class=HTMLResponse)
async def new_post_submit(
    request: Request,
    db: DBDep,
    current_user: WebUser,
    content: str = Form(...),
    tag_ids: List[int] = Form(default=[]),
):
    if not current_user:
        return RedirectResponse("/login", status_code=303)
    data = PostCreate(content=content, tag_ids=tag_ids)
    await post_crud.create(db, data, current_user.id)
    return redirect("/", message="Пост успешно создан")


@router.get("/posts/{post_id}/edit", response_class=HTMLResponse)
async def edit_post_form(request: Request, post_id: int, db: DBDep, current_user: WebUser):
    if not current_user:
        return RedirectResponse("/login", status_code=303)
    post = await post_crud.get_by_id(db, post_id)
    if not post:
        return redirect("/", message="Пост не найден")
    is_admin = "ROLE_ADMIN" in current_user.roles
    if post.author_id != current_user.id and not is_admin:
        return redirect("/", message="Недостаточно прав")
    all_tags = await tag_crud.get_all(db)
    return templates.TemplateResponse(
        "posts/edit.html",
        {"request": request, "user": current_user, "post": post, "tags": all_tags},
    )


@router.post("/posts/{post_id}/edit", response_class=HTMLResponse)
async def edit_post_submit(
    request: Request,
    post_id: int,
    db: DBDep,
    current_user: WebUser,
    content: str = Form(...),
    tag_ids: List[int] = Form(default=[]),
):
    if not current_user:
        return RedirectResponse("/login", status_code=303)
    post = await post_crud.get_by_id(db, post_id)
    if not post:
        return redirect("/", message="Пост не найден")
    is_admin = "ROLE_ADMIN" in current_user.roles
    if post.author_id != current_user.id and not is_admin:
        return redirect("/", message="Недостаточно прав")
    data = PostUpdate(content=content, tag_ids=tag_ids)
    await post_crud.update_post(db, post, data)
    return redirect("/", message="Пост успешно обновлён")


@router.post("/posts/{post_id}/delete", response_class=HTMLResponse)
async def delete_post(request: Request, post_id: int, db: DBDep, current_user: WebUser):
    if not current_user:
        return RedirectResponse("/login", status_code=303)
    post = await post_crud.get_by_id(db, post_id)
    if not post:
        return redirect("/", message="Пост не найден")
    is_admin = "ROLE_ADMIN" in current_user.roles
    if post.author_id != current_user.id and not is_admin:
        return redirect("/", message="Недостаточно прав")
    await post_crud.delete(db, post)
    return redirect("/", message="Пост удалён")


@router.post("/posts/{post_id}/favorite", response_class=HTMLResponse)
async def add_favorite(request: Request, post_id: int, db: DBDep, current_user: WebUser):
    if not current_user:
        return RedirectResponse("/login", status_code=303)
    post = await post_crud.get_by_id(db, post_id)
    if post:
        await post_crud.add_to_favorites(db, post, current_user)
    referer = request.headers.get("referer", "/")
    return RedirectResponse(referer, status_code=303)


@router.post("/posts/{post_id}/unfavorite", response_class=HTMLResponse)
async def remove_favorite(request: Request, post_id: int, db: DBDep, current_user: WebUser):
    if not current_user:
        return RedirectResponse("/login", status_code=303)
    post = await post_crud.get_by_id(db, post_id)
    if post:
        await post_crud.remove_from_favorites(db, post, current_user)
    referer = request.headers.get("referer", "/")
    return RedirectResponse(referer, status_code=303)
