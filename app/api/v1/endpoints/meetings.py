from typing import List
from fastapi import APIRouter, Depends

from app.api.deps import DBDep, CurrentUser, require_roles
from app.models.user import User
from app.core.exceptions import NotFoundError
from app.crud import meeting as meeting_crud
from app.crud import group as group_crud
from app.schemas.meeting import MeetingCreate, MeetingUpdate, MeetingRead

router = APIRouter(prefix="/meetings", tags=["meetings"])


@router.get("/group/{group_id}", response_model=List[MeetingRead])
async def list_meetings(group_id: int, db: DBDep, current_user: CurrentUser):
    return await meeting_crud.get_by_group(db, group_id)


@router.post("/", response_model=MeetingRead, status_code=201)
async def create_meeting(
    data: MeetingCreate,
    db: DBDep,
    _: User = Depends(require_roles("ROLE_TEACHER", "ROLE_ADMIN")),
):
    group = await group_crud.get_by_id(db, data.group_id)
    if not group:
        raise NotFoundError("Группа не найдена")
    return await meeting_crud.create(db, data)


@router.get("/{meeting_id}", response_model=MeetingRead)
async def get_meeting(meeting_id: int, db: DBDep, current_user: CurrentUser):
    meeting = await meeting_crud.get_by_id(db, meeting_id)
    if not meeting:
        raise NotFoundError("Встреча не найдена")
    return meeting


@router.patch("/{meeting_id}", response_model=MeetingRead)
async def update_meeting(
    meeting_id: int,
    data: MeetingUpdate,
    db: DBDep,
    _: User = Depends(require_roles("ROLE_TEACHER", "ROLE_ADMIN")),
):
    meeting = await meeting_crud.get_by_id(db, meeting_id)
    if not meeting:
        raise NotFoundError("Встреча не найдена")
    return await meeting_crud.update_meeting(db, meeting, data)


@router.delete("/{meeting_id}", status_code=204)
async def delete_meeting(
    meeting_id: int,
    db: DBDep,
    _: User = Depends(require_roles("ROLE_TEACHER", "ROLE_ADMIN")),
):
    meeting = await meeting_crud.get_by_id(db, meeting_id)
    if not meeting:
        raise NotFoundError("Встреча не найдена")
    await meeting_crud.delete(db, meeting)
