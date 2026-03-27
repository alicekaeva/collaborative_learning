from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.content.models.task import Task
from app.modules.content.schemas.task import TaskCreate, TaskUpdate


async def get_by_id(db: AsyncSession, task_id: int) -> Optional[Task]:
    result = await db.execute(select(Task).where(Task.id == task_id))
    return result.scalar_one_or_none()


async def get_by_group(db: AsyncSession, group_id: int) -> List[Task]:
    result = await db.execute(select(Task).where(Task.creator_id == group_id))
    return list(result.scalars().all())


async def create(db: AsyncSession, data: TaskCreate) -> Task:
    task = Task(
        name=data.name,
        link=data.link,
        deadline=data.deadline,
        points=data.points,
        creator_id=data.group_id,
    )
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task


async def update_task(db: AsyncSession, task: Task, data: TaskUpdate) -> Task:
    if data.name is not None:
        task.name = data.name
    if data.link is not None:
        task.link = data.link
    if data.deadline is not None:
        task.deadline = data.deadline
    if data.points is not None:
        task.points = data.points
    await db.commit()
    await db.refresh(task)
    return task


async def delete(db: AsyncSession, task: Task) -> None:
    await db.delete(task)
    await db.commit()
