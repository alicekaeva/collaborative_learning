from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.content.models.meeting import Meeting
from app.modules.content.schemas.meeting import MeetingCreate, MeetingUpdate


async def get_by_id(db: AsyncSession, meeting_id: int) -> Optional[Meeting]:
    result = await db.execute(select(Meeting).where(Meeting.id == meeting_id))
    return result.scalar_one_or_none()


async def get_by_group(db: AsyncSession, group_id: int) -> List[Meeting]:
    result = await db.execute(select(Meeting).where(Meeting.creator_id == group_id))
    return list(result.scalars().all())


async def create(db: AsyncSession, data: MeetingCreate) -> Meeting:
    meeting = Meeting(
        name=data.name,
        agenda=data.agenda,
        link=data.link,
        held_on=data.held_on,
        creator_id=data.group_id,
    )
    db.add(meeting)
    await db.commit()
    await db.refresh(meeting)
    return meeting


async def update_meeting(db: AsyncSession, meeting: Meeting, data: MeetingUpdate) -> Meeting:
    if data.name is not None:
        meeting.name = data.name
    if data.agenda is not None:
        meeting.agenda = data.agenda
    if data.link is not None:
        meeting.link = data.link
    if data.held_on is not None:
        meeting.held_on = data.held_on
    await db.commit()
    await db.refresh(meeting)
    return meeting


async def delete(db: AsyncSession, meeting: Meeting) -> None:
    await db.delete(meeting)
    await db.commit()
