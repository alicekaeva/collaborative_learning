from typing import List
from fastapi import APIRouter, Depends

from app.api.deps import DBDep, CurrentUser, require_roles
from app.models.user import User
from app.core.exceptions import NotFoundError, ForbiddenError
from app.crud import goal as goal_crud
from app.crud import group as group_crud
from app.schemas.goal import GoalCreate, GoalUpdate, GoalRead
from app.schemas.common import Message

router = APIRouter(prefix="/goals", tags=["goals"])


@router.get("/group/{group_id}", response_model=List[GoalRead])
async def list_goals(group_id: int, db: DBDep, current_user: CurrentUser):
    return await goal_crud.get_by_group(db, group_id)


@router.post("/", response_model=GoalRead, status_code=201)
async def create_goal(
    data: GoalCreate,
    db: DBDep,
    _: User = Depends(require_roles("ROLE_TEACHER", "ROLE_ADMIN")),
):
    group = await group_crud.get_by_id(db, data.group_id)
    if not group:
        raise NotFoundError("Группа не найдена")
    return await goal_crud.create(db, data)


@router.get("/{goal_id}", response_model=GoalRead)
async def get_goal(goal_id: int, db: DBDep, current_user: CurrentUser):
    goal = await goal_crud.get_by_id(db, goal_id)
    if not goal:
        raise NotFoundError("Цель не найдена")
    return goal


@router.patch("/{goal_id}", response_model=GoalRead)
async def update_goal(
    goal_id: int,
    data: GoalUpdate,
    db: DBDep,
    _: User = Depends(require_roles("ROLE_TEACHER", "ROLE_ADMIN")),
):
    goal = await goal_crud.get_by_id(db, goal_id)
    if not goal:
        raise NotFoundError("Цель не найдена")
    return await goal_crud.update_goal(db, goal, data)


@router.post("/{goal_id}/complete", response_model=GoalRead)
async def complete_goal(
    goal_id: int,
    db: DBDep,
    _: User = Depends(require_roles("ROLE_TEACHER", "ROLE_ADMIN")),
):
    goal = await goal_crud.get_by_id(db, goal_id)
    if not goal:
        raise NotFoundError("Цель не найдена")
    return await goal_crud.set_completed(db, goal, True)


@router.post("/{goal_id}/uncomplete", response_model=GoalRead)
async def uncomplete_goal(
    goal_id: int,
    db: DBDep,
    _: User = Depends(require_roles("ROLE_TEACHER", "ROLE_ADMIN")),
):
    goal = await goal_crud.get_by_id(db, goal_id)
    if not goal:
        raise NotFoundError("Цель не найдена")
    return await goal_crud.set_completed(db, goal, False)


@router.delete("/{goal_id}", response_model=Message)
async def delete_goal(
    goal_id: int,
    db: DBDep,
    _: User = Depends(require_roles("ROLE_TEACHER", "ROLE_ADMIN")),
):
    goal = await goal_crud.get_by_id(db, goal_id)
    if not goal:
        raise NotFoundError("Цель не найдена")
    await goal_crud.delete(db, goal)
    return Message(detail="Цель удалена")
