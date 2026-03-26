from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse, HTMLResponse

from app.api.deps import DBDep
from app.crud import message as message_crud, user as user_crud
from app.web.deps import WebUser
from app.web.utils import templates, redirect

router = APIRouter(tags=["web:messages"])


def _get_flash(request: Request) -> str | None:
    return request.cookies.get("flash_message")


def _clear_flash(response) -> None:
    response.delete_cookie("flash_message")


@router.get("/messages", response_class=HTMLResponse)
async def messages_list(request: Request, db: DBDep, current_user: WebUser):
    if not current_user:
        return RedirectResponse("/login", status_code=303)

    dialog_messages = await message_crud.get_user_dialogs(db, current_user.id)

    # Gather the partner user for each dialog message
    dialogs = []
    for msg in dialog_messages:
        partner_id = msg.receiver_id if msg.sender_id == current_user.id else msg.sender_id
        if partner_id:
            partner = await user_crud.get_by_id(db, partner_id)
            dialogs.append({"last_message": msg, "partner": partner})

    flash = _get_flash(request)
    response = templates.TemplateResponse(
        "messages/list.html",
        {
            "request": request,
            "user": current_user,
            "dialogs": dialogs,
            "flash": flash,
        },
    )
    if flash:
        _clear_flash(response)
    return response


@router.get("/messages/dialog/{user_id}", response_class=HTMLResponse)
async def view_dialog(request: Request, user_id: int, db: DBDep, current_user: WebUser):
    if not current_user:
        return RedirectResponse("/login", status_code=303)

    partner = await user_crud.get_by_id(db, user_id)
    if not partner:
        return redirect("/messages", message="Пользователь не найден")

    messages = await message_crud.get_dialog(db, current_user.id, user_id)

    flash = _get_flash(request)
    response = templates.TemplateResponse(
        "messages/dialog.html",
        {
            "request": request,
            "user": current_user,
            "partner": partner,
            "messages": messages,
            "flash": flash,
        },
    )
    if flash:
        _clear_flash(response)
    return response


@router.post("/messages/send", response_class=HTMLResponse)
async def send_message(
    request: Request,
    db: DBDep,
    current_user: WebUser,
    receiver_id: int = Form(...),
    content: str = Form(...),
):
    if not current_user:
        return RedirectResponse("/login", status_code=303)

    receiver = await user_crud.get_by_id(db, receiver_id)
    if not receiver:
        return redirect("/messages", message="Получатель не найден")

    await message_crud.send_direct(db, content=content, sender_id=current_user.id, receiver_id=receiver_id)
    return RedirectResponse(f"/messages/dialog/{receiver_id}", status_code=303)


@router.get("/messages/group/{group_id}", response_class=HTMLResponse)
async def group_chat_redirect(request: Request, group_id: int, current_user: WebUser):
    if not current_user:
        return RedirectResponse("/login", status_code=303)
    return RedirectResponse(f"/learning/groups/{group_id}", status_code=303)


@router.post("/messages/{message_id}/pin", response_class=HTMLResponse)
async def pin_message(request: Request, message_id: int, db: DBDep, current_user: WebUser):
    if not current_user:
        return RedirectResponse("/login", status_code=303)

    message = await message_crud.get_by_id(db, message_id)
    if not message:
        referer = request.headers.get("referer", "/messages")
        return RedirectResponse(referer, status_code=303)

    await message_crud.pin_message(db, message)
    referer = request.headers.get("referer", "/messages")
    return RedirectResponse(referer, status_code=303)


@router.post("/messages/{message_id}/unpin", response_class=HTMLResponse)
async def unpin_message(request: Request, message_id: int, db: DBDep, current_user: WebUser):
    if not current_user:
        return RedirectResponse("/login", status_code=303)

    message = await message_crud.get_by_id(db, message_id)
    if not message:
        referer = request.headers.get("referer", "/messages")
        return RedirectResponse(referer, status_code=303)

    await message_crud.unpin_message(db, message)
    referer = request.headers.get("referer", "/messages")
    return RedirectResponse(referer, status_code=303)


@router.post("/messages/{message_id}/delete", response_class=HTMLResponse)
async def delete_message(request: Request, message_id: int, db: DBDep, current_user: WebUser):
    if not current_user:
        return RedirectResponse("/login", status_code=303)

    message = await message_crud.get_by_id(db, message_id)
    if message:
        # Only sender or admin can delete
        is_admin = "ROLE_ADMIN" in current_user.roles
        if message.sender_id == current_user.id or is_admin:
            await message_crud.delete(db, message)

    referer = request.headers.get("referer", "/messages")
    return RedirectResponse(referer, status_code=303)
