from typing import List
from fastapi import APIRouter, Depends

from app.api.deps import DBDep, CurrentUser, require_roles
from app.models.user import User
from app.core.exceptions import NotFoundError
from app.crud import task as task_crud
from app.crud import group as group_crud
from app.schemas.task import TaskCreate, TaskUpdate, TaskRead

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("/group/{group_id}", response_model=List[TaskRead])
async def list_tasks(group_id: int, db: DBDep, current_user: CurrentUser):
    return await task_crud.get_by_group(db, group_id)


@router.post("/", response_model=TaskRead, status_code=201)
async def create_task(
    data: TaskCreate,
    db: DBDep,
    _: User = Depends(require_roles("ROLE_TEACHER", "ROLE_ADMIN")),
):
    group = await group_crud.get_by_id(db, data.group_id)
    if not group:
        raise NotFoundError("Группа не найдена")
    return await task_crud.create(db, data)


@router.get("/{task_id}", response_model=TaskRead)
async def get_task(task_id: int, db: DBDep, current_user: CurrentUser):
    task = await task_crud.get_by_id(db, task_id)
    if not task:
        raise NotFoundError("Задание не найдено")
    return task


@router.patch("/{task_id}", response_model=TaskRead)
async def update_task(
    task_id: int,
    data: TaskUpdate,
    db: DBDep,
    _: User = Depends(require_roles("ROLE_TEACHER", "ROLE_ADMIN")),
):
    task = await task_crud.get_by_id(db, task_id)
    if not task:
        raise NotFoundError("Задание не найдено")
    return await task_crud.update_task(db, task, data)


@router.delete("/{task_id}", status_code=204)
async def delete_task(
    task_id: int,
    db: DBDep,
    _: User = Depends(require_roles("ROLE_TEACHER", "ROLE_ADMIN")),
):
    task = await task_crud.get_by_id(db, task_id)
    if not task:
        raise NotFoundError("Задание не найдено")
    await task_crud.delete(db, task)
