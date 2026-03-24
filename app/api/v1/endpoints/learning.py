from typing import List
from fastapi import APIRouter

from app.api.deps import DBDep, CurrentUser
from app.core.exceptions import NotFoundError, ForbiddenError
from app.crud import group as group_crud
from app.crud import message as message_crud
from app.crud import goal as goal_crud
from app.crud import task as task_crud
from app.crud import meeting as meeting_crud
from app.crud import material as material_crud
from app.schemas.group import GroupRead
from app.schemas.message import MessageRead, SendGroupMessageRequest
from app.schemas.goal import GoalRead
from app.schemas.task import TaskRead
from app.schemas.meeting import MeetingRead
from app.schemas.material import MaterialRead
from pydantic import BaseModel

router = APIRouter(prefix="/learning", tags=["learning"])


class LearningGroupDetail(BaseModel):
    group: GroupRead
    messages: List[MessageRead] = []
    goals: List[GoalRead] = []
    tasks: List[TaskRead] = []
    meetings: List[MeetingRead] = []
    materials: List[MaterialRead] = []


@router.get("/groups", response_model=List[GroupRead])
async def my_learning_groups(db: DBDep, current_user: CurrentUser):
    """Get all groups the current user belongs to."""
    return await group_crud.get_user_groups(db, current_user)


@router.get("/groups/{group_id}", response_model=LearningGroupDetail)
async def learning_group_detail(group_id: int, db: DBDep, current_user: CurrentUser):
    """Get full learning context for a group (chat, goals, tasks, meetings, materials)."""
    group = await group_crud.get_by_id(db, group_id)
    if not group:
        raise NotFoundError("Группа не найдена")

    # Verify user membership
    role = await group_crud.get_user_role_in_group(db, group, current_user)
    if not role:
        raise ForbiddenError("Вы не состоите в этой группе")

    messages = await message_crud.get_group_chat(db, group_id)
    goals = await goal_crud.get_by_group(db, group_id)
    tasks = await task_crud.get_by_group(db, group_id)
    meetings = await meeting_crud.get_by_group(db, group_id)
    materials = await material_crud.get_by_group(db, group_id)

    return LearningGroupDetail(
        group=GroupRead.model_validate(group),
        messages=[MessageRead.model_validate(m) for m in messages],
        goals=[GoalRead.model_validate(g) for g in goals],
        tasks=[TaskRead.model_validate(t) for t in tasks],
        meetings=[MeetingRead.model_validate(m) for m in meetings],
        materials=[MaterialRead.model_validate(m) for m in materials],
    )


@router.post("/groups/{group_id}/chat", response_model=MessageRead, status_code=201)
async def send_chat_message(
    group_id: int,
    data: SendGroupMessageRequest,
    db: DBDep,
    current_user: CurrentUser,
):
    group = await group_crud.get_by_id(db, group_id)
    if not group:
        raise NotFoundError("Группа не найдена")

    role = await group_crud.get_user_role_in_group(db, group, current_user)
    if not role:
        raise ForbiddenError("Вы не состоите в этой группе")

    return await message_crud.send_group(db, data.content, current_user.id, group_id)
