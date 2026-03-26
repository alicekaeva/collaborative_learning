from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse, HTMLResponse

from app.api.deps import DBDep
from app.crud import group as group_crud, message as message_crud, goal as goal_crud
from app.crud import task as task_crud, meeting as meeting_crud, material as material_crud
from app.web.deps import WebUser
from app.web.utils import templates, redirect

router = APIRouter(tags=["web:learning"])


def _get_flash(request: Request) -> str | None:
    return request.cookies.get("flash_message")


def _clear_flash(response) -> None:
    response.delete_cookie("flash_message")


@router.get("/learning", response_class=HTMLResponse)
async def learning_home(request: Request, db: DBDep, current_user: WebUser):
    if not current_user:
        return RedirectResponse("/login", status_code=303)

    user_groups = await group_crud.get_user_groups(db, current_user)

    flash = _get_flash(request)
    response = templates.TemplateResponse(
        "learning/home.html",
        {
            "request": request,
            "user": current_user,
            "groups": user_groups,
            "flash": flash,
        },
    )
    if flash:
        _clear_flash(response)
    return response


@router.get("/learning/groups/{group_id}", response_class=HTMLResponse)
async def group_workspace(request: Request, group_id: int, db: DBDep, current_user: WebUser):
    if not current_user:
        return RedirectResponse("/login", status_code=303)

    group = await group_crud.get_by_id(db, group_id)
    if not group:
        return redirect("/learning", message="Группа не найдена")

    # Check membership
    user_role = await group_crud.get_user_role_in_group(db, group, current_user)
    if not user_role:
        return redirect("/learning", message="Вы не являетесь участником этой группы")

    # Load all workspace data
    chat_messages = await message_crud.get_group_chat(db, group_id)
    goals = await goal_crud.get_by_group(db, group_id)
    tasks = await task_crud.get_by_group(db, group_id)
    meetings = await meeting_crud.get_by_group(db, group_id)
    materials = await material_crud.get_by_group(db, group_id)

    flash = _get_flash(request)
    response = templates.TemplateResponse(
        "learning/workspace.html",
        {
            "request": request,
            "user": current_user,
            "group": group,
            "user_role": user_role,
            "chat_messages": chat_messages,
            "goals": goals,
            "tasks": tasks,
            "meetings": meetings,
            "materials": materials,
            "flash": flash,
        },
    )
    if flash:
        _clear_flash(response)
    return response


@router.post("/learning/groups/{group_id}/chat", response_class=HTMLResponse)
async def send_group_chat(
    request: Request,
    group_id: int,
    db: DBDep,
    current_user: WebUser,
    content: str = Form(...),
):
    if not current_user:
        return RedirectResponse("/login", status_code=303)

    group = await group_crud.get_by_id(db, group_id)
    if not group:
        return redirect("/learning", message="Группа не найдена")

    user_role = await group_crud.get_user_role_in_group(db, group, current_user)
    if not user_role:
        return redirect("/learning", message="Вы не являетесь участником этой группы")

    await message_crud.send_group(db, content=content, sender_id=current_user.id, group_id=group_id)
    return RedirectResponse(f"/learning/groups/{group_id}", status_code=303)
