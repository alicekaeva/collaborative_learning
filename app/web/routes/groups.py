from typing import Optional, List

from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse, HTMLResponse

from app.api.deps import DBDep
from app.crud import group as group_crud, tag as tag_crud, category as category_crud, user as user_crud
from app.schemas.group import GroupCreate, GroupUpdate
from app.web.deps import WebUser
from app.web.utils import templates, redirect

router = APIRouter(tags=["web:groups"])


def _get_flash(request: Request) -> str | None:
    return request.cookies.get("flash_message")


def _clear_flash(response) -> None:
    response.delete_cookie("flash_message")


@router.get("/groups", response_class=HTMLResponse)
async def group_list(
    request: Request,
    db: DBDep,
    current_user: WebUser,
    tag_id: Optional[int] = None,
    category_id: Optional[int] = None,
):
    if tag_id:
        groups = await group_crud.get_by_tag(db, tag_id)
    elif category_id:
        groups = await group_crud.get_by_category(db, category_id)
    else:
        groups = await group_crud.get_all(db)

    all_tags = await tag_crud.get_all(db)
    all_categories = await category_crud.get_all(db)

    flash = _get_flash(request)
    response = templates.TemplateResponse(
        "groups/list.html",
        {
            "request": request,
            "user": current_user,
            "groups": groups,
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


@router.get("/groups/recommended", response_class=HTMLResponse)
async def groups_recommended(request: Request, db: DBDep, current_user: WebUser):
    if not current_user:
        return RedirectResponse("/login", status_code=303)
    tag_ids = [t.id for t in current_user.tags]
    groups = await group_crud.get_recommended(db, tag_ids)
    return templates.TemplateResponse(
        "groups/recommended.html",
        {"request": request, "user": current_user, "groups": groups},
    )


@router.get("/groups/new", response_class=HTMLResponse)
async def new_group_form(request: Request, db: DBDep, current_user: WebUser):
    if not current_user:
        return RedirectResponse("/login", status_code=303)
    if not current_user.admin_profile:
        return redirect("/groups", message="Только администраторы могут создавать группы")
    all_tags = await tag_crud.get_all(db)
    return templates.TemplateResponse(
        "groups/new.html",
        {"request": request, "user": current_user, "tags": all_tags},
    )


@router.post("/groups/new", response_class=HTMLResponse)
async def new_group_submit(
    request: Request,
    db: DBDep,
    current_user: WebUser,
    name: str = Form(...),
    info: Optional[str] = Form(default=None),
    required_teachers: int = Form(default=1),
    required_students: int = Form(default=1),
    tag_ids: List[int] = Form(default=[]),
):
    if not current_user:
        return RedirectResponse("/login", status_code=303)
    if not current_user.admin_profile:
        return redirect("/groups", message="Только администраторы могут создавать группы")
    data = GroupCreate(
        name=name,
        info=info,
        required_teachers=required_teachers,
        required_students=required_students,
        tag_ids=tag_ids,
    )
    group = await group_crud.create(db, data, current_user.admin_profile)
    return redirect(f"/groups/{group.id}", message="Группа успешно создана")


@router.get("/groups/{group_id}", response_class=HTMLResponse)
async def group_detail(request: Request, group_id: int, db: DBDep, current_user: WebUser):
    group = await group_crud.get_by_id(db, group_id)
    if not group:
        return redirect("/groups", message="Группа не найдена")

    user_role = None
    if current_user:
        user_role = await group_crud.get_user_role_in_group(db, group, current_user)

    flash = _get_flash(request)
    response = templates.TemplateResponse(
        "groups/detail.html",
        {
            "request": request,
            "user": current_user,
            "group": group,
            "user_role": user_role,
            "flash": flash,
        },
    )
    if flash:
        _clear_flash(response)
    return response


@router.get("/groups/{group_id}/edit", response_class=HTMLResponse)
async def edit_group_form(request: Request, group_id: int, db: DBDep, current_user: WebUser):
    if not current_user:
        return RedirectResponse("/login", status_code=303)
    group = await group_crud.get_by_id(db, group_id)
    if not group:
        return redirect("/groups", message="Группа не найдена")
    if not current_user.admin_profile or group.administrator_id != current_user.admin_profile.id:
        return redirect(f"/groups/{group_id}", message="Недостаточно прав")
    all_tags = await tag_crud.get_all(db)
    return templates.TemplateResponse(
        "groups/edit.html",
        {"request": request, "user": current_user, "group": group, "tags": all_tags},
    )


@router.post("/groups/{group_id}/edit", response_class=HTMLResponse)
async def edit_group_submit(
    request: Request,
    group_id: int,
    db: DBDep,
    current_user: WebUser,
    name: str = Form(...),
    info: Optional[str] = Form(default=None),
    required_teachers: int = Form(default=1),
    required_students: int = Form(default=1),
    tag_ids: List[int] = Form(default=[]),
):
    if not current_user:
        return RedirectResponse("/login", status_code=303)
    group = await group_crud.get_by_id(db, group_id)
    if not group:
        return redirect("/groups", message="Группа не найдена")
    if not current_user.admin_profile or group.administrator_id != current_user.admin_profile.id:
        return redirect(f"/groups/{group_id}", message="Недостаточно прав")
    data = GroupUpdate(
        name=name,
        info=info,
        required_teachers=required_teachers,
        required_students=required_students,
        tag_ids=tag_ids,
    )
    await group_crud.update_group(db, group, data)
    return redirect(f"/groups/{group_id}", message="Группа успешно обновлена")


@router.post("/groups/{group_id}/delete", response_class=HTMLResponse)
async def delete_group(request: Request, group_id: int, db: DBDep, current_user: WebUser):
    if not current_user:
        return RedirectResponse("/login", status_code=303)
    group = await group_crud.get_by_id(db, group_id)
    if not group:
        return redirect("/groups", message="Группа не найдена")
    if not current_user.admin_profile or group.administrator_id != current_user.admin_profile.id:
        return redirect(f"/groups/{group_id}", message="Недостаточно прав")
    await group_crud.delete(db, group)
    return redirect("/groups", message="Группа удалена")


@router.get("/groups/{group_id}/management", response_class=HTMLResponse)
async def group_management(request: Request, group_id: int, db: DBDep, current_user: WebUser):
    if not current_user:
        return RedirectResponse("/login", status_code=303)
    group = await group_crud.get_by_id(db, group_id)
    if not group:
        return redirect("/groups", message="Группа не найдена")
    if not current_user.admin_profile or group.administrator_id != current_user.admin_profile.id:
        return redirect(f"/groups/{group_id}", message="Недостаточно прав")

    flash = _get_flash(request)
    response = templates.TemplateResponse(
        "groups/management.html",
        {
            "request": request,
            "user": current_user,
            "group": group,
            "flash": flash,
        },
    )
    if flash:
        _clear_flash(response)
    return response


@router.post("/groups/{group_id}/add-user", response_class=HTMLResponse)
async def add_user_to_group(
    request: Request,
    group_id: int,
    db: DBDep,
    current_user: WebUser,
    user_id: int = Form(...),
    role: str = Form(...),
):
    if not current_user:
        return RedirectResponse("/login", status_code=303)
    group = await group_crud.get_by_id(db, group_id)
    if not group:
        return redirect("/groups", message="Группа не найдена")
    if not current_user.admin_profile or group.administrator_id != current_user.admin_profile.id:
        return redirect(f"/groups/{group_id}", message="Недостаточно прав")

    target_user = await user_crud.get_by_id(db, user_id)
    if not target_user:
        return redirect(f"/groups/{group_id}/management", message="Пользователь не найден")

    if role == "teacher":
        if not target_user.teacher_profile:
            return redirect(f"/groups/{group_id}/management", message="У пользователя нет профиля преподавателя")
        await group_crud.add_teacher(db, group, target_user.teacher_profile)
    elif role == "student":
        if not target_user.student_profile:
            return redirect(f"/groups/{group_id}/management", message="У пользователя нет профиля студента")
        await group_crud.add_student(db, group, target_user.student_profile)
    else:
        return redirect(f"/groups/{group_id}/management", message="Неверная роль")

    return redirect(f"/groups/{group_id}/management", message="Пользователь добавлен в группу")


@router.post("/groups/{group_id}/remove-user", response_class=HTMLResponse)
async def remove_user_from_group(
    request: Request,
    group_id: int,
    db: DBDep,
    current_user: WebUser,
    user_id: int = Form(...),
    role: str = Form(...),
):
    if not current_user:
        return RedirectResponse("/login", status_code=303)
    group = await group_crud.get_by_id(db, group_id)
    if not group:
        return redirect("/groups", message="Группа не найдена")
    if not current_user.admin_profile or group.administrator_id != current_user.admin_profile.id:
        return redirect(f"/groups/{group_id}", message="Недостаточно прав")

    target_user = await user_crud.get_by_id(db, user_id)
    if not target_user:
        return redirect(f"/groups/{group_id}/management", message="Пользователь не найден")

    if role == "teacher":
        if target_user.teacher_profile:
            await group_crud.remove_teacher(db, group, target_user.teacher_profile)
    elif role == "student":
        if target_user.student_profile:
            await group_crud.remove_student(db, group, target_user.student_profile)

    return redirect(f"/groups/{group_id}/management", message="Пользователь удалён из группы")


@router.post("/groups/{group_id}/enroll", response_class=HTMLResponse)
async def enroll_in_group(
    request: Request,
    group_id: int,
    db: DBDep,
    current_user: WebUser,
):
    if not current_user:
        return RedirectResponse("/login", status_code=303)
    group = await group_crud.get_by_id(db, group_id)
    if not group:
        return redirect("/groups", message="Группа не найдена")

    # Enroll as student if the user has a student profile, otherwise as teacher
    if current_user.student_profile:
        await group_crud.add_student(db, group, current_user.student_profile)
        return redirect(f"/groups/{group_id}", message="Запрос на вступление отправлен")
    elif current_user.teacher_profile:
        await group_crud.add_teacher(db, group, current_user.teacher_profile)
        return redirect(f"/groups/{group_id}", message="Запрос на вступление отправлен")
    else:
        return redirect(f"/groups/{group_id}", message="У вас нет профиля студента или преподавателя")
