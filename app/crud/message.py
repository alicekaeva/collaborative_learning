from typing import Optional, List
from sqlalchemy import select, desc, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.message import Message
from app.models.user import User


async def get_by_id(db: AsyncSession, message_id: int) -> Optional[Message]:
    result = await db.execute(select(Message).where(Message.id == message_id))
    return result.scalar_one_or_none()


async def send_direct(db: AsyncSession, content: str, sender_id: int, receiver_id: int) -> Message:
    message = Message(content=content, sender_id=sender_id, receiver_id=receiver_id)
    db.add(message)
    await db.commit()
    await db.refresh(message)
    return message


async def send_group(db: AsyncSession, content: str, sender_id: int, group_id: int) -> Message:
    message = Message(content=content, sender_id=sender_id, receiving_group_id=group_id)
    db.add(message)
    await db.commit()
    await db.refresh(message)
    return message


async def get_dialog(db: AsyncSession, user1_id: int, user2_id: int) -> List[Message]:
    result = await db.execute(
        select(Message)
        .where(
            or_(
                and_(Message.sender_id == user1_id, Message.receiver_id == user2_id),
                and_(Message.sender_id == user2_id, Message.receiver_id == user1_id),
            )
        )
        .order_by(Message.sending_date)
    )
    return list(result.scalars().all())


async def get_group_chat(db: AsyncSession, group_id: int) -> List[Message]:
    result = await db.execute(
        select(Message)
        .where(Message.receiving_group_id == group_id)
        .order_by(Message.sending_date)
    )
    return list(result.scalars().all())


async def get_user_dialogs(db: AsyncSession, user_id: int) -> List[Message]:
    """Get the latest message for each unique dialog partner."""
    # Subquery to get distinct conversation partners
    result = await db.execute(
        select(Message)
        .where(
            or_(
                Message.sender_id == user_id,
                Message.receiver_id == user_id,
            ),
            Message.receiving_group_id.is_(None),
        )
        .order_by(desc(Message.sending_date))
    )
    messages = list(result.scalars().all())

    # Deduplicate by conversation partner
    seen_partners: set[int] = set()
    unique = []
    for msg in messages:
        partner_id = msg.receiver_id if msg.sender_id == user_id else msg.sender_id
        if partner_id and partner_id not in seen_partners:
            seen_partners.add(partner_id)
            unique.append(msg)
    return unique


async def pin_message(db: AsyncSession, message: Message) -> Message:
    message.is_pinned = True
    await db.commit()
    await db.refresh(message)
    return message


async def unpin_message(db: AsyncSession, message: Message) -> Message:
    message.is_pinned = False
    await db.commit()
    await db.refresh(message)
    return message


async def delete(db: AsyncSession, message: Message) -> None:
    await db.delete(message)
    await db.commit()
