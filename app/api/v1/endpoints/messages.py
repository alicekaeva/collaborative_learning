from typing import List
from fastapi import APIRouter
from sqlalchemy import select

from app.api.deps import DBDep, CurrentUser
from app.core.exceptions import NotFoundError, ForbiddenError
from app.crud import message as message_crud
from app.models.user import User as UserModel
from app.schemas.message import (
    MessageRead, SendDirectMessageRequest, SendGroupMessageRequest, DialogPreview
)
from app.schemas.common import Message as ResponseMessage
from app.schemas.user import UserShort

router = APIRouter(prefix="/messages", tags=["messages"])


@router.get("/dialogs", response_model=List[DialogPreview])
async def list_dialogs(db: DBDep, current_user: CurrentUser):
    messages = await message_crud.get_user_dialogs(db, current_user.id)

    partner_ids = list({
        msg.receiver_id if msg.sender_id == current_user.id else msg.sender_id
        for msg in messages
    })
    partners_result = await db.execute(select(UserModel).where(UserModel.id.in_(partner_ids)))
    partners = {u.id: u for u in partners_result.scalars().all()}

    result = []
    for msg in messages:
        partner_id = msg.receiver_id if msg.sender_id == current_user.id else msg.sender_id
        partner = partners.get(partner_id)
        if partner:
            result.append(DialogPreview(
                user=UserShort.model_validate(partner),
                last_message=msg.content[:100],
                last_message_date=msg.sending_date,
            ))
    return result


@router.get("/dialog/{user_id}", response_model=List[MessageRead])
async def get_dialog(user_id: int, db: DBDep, current_user: CurrentUser):
    return await message_crud.get_dialog(db, current_user.id, user_id)


@router.post("/direct", response_model=MessageRead, status_code=201)
async def send_direct(data: SendDirectMessageRequest, db: DBDep, current_user: CurrentUser):
    receiver = await user_crud.get_by_id(db, data.receiver_id)
    if not receiver:
        raise NotFoundError("Получатель не найден")
    return await message_crud.send_direct(db, data.content, current_user.id, data.receiver_id)


@router.post("/group", response_model=MessageRead, status_code=201)
async def send_group_message(data: SendGroupMessageRequest, db: DBDep, current_user: CurrentUser):
    return await message_crud.send_group(db, data.content, current_user.id, data.receiving_group_id)


@router.get("/group/{group_id}", response_model=List[MessageRead])
async def group_chat(group_id: int, db: DBDep, current_user: CurrentUser):
    return await message_crud.get_group_chat(db, group_id)


@router.post("/{message_id}/pin", response_model=MessageRead)
async def pin_message(message_id: int, db: DBDep, current_user: CurrentUser):
    msg = await message_crud.get_by_id(db, message_id)
    if not msg:
        raise NotFoundError("Сообщение не найдено")
    return await message_crud.pin_message(db, msg)


@router.post("/{message_id}/unpin", response_model=MessageRead)
async def unpin_message(message_id: int, db: DBDep, current_user: CurrentUser):
    msg = await message_crud.get_by_id(db, message_id)
    if not msg:
        raise NotFoundError("Сообщение не найдено")
    return await message_crud.unpin_message(db, msg)


@router.delete("/{message_id}", response_model=ResponseMessage)
async def delete_message(message_id: int, db: DBDep, current_user: CurrentUser):
    msg = await message_crud.get_by_id(db, message_id)
    if not msg:
        raise NotFoundError("Сообщение не найдено")
    if msg.sender_id != current_user.id and "ROLE_ADMIN" not in current_user.roles:
        raise ForbiddenError("Нет доступа")
    await message_crud.delete(db, msg)
    return ResponseMessage(detail="Сообщение удалено")
