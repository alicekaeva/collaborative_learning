from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.goal import Goal
from app.schemas.goal import GoalCreate, GoalUpdate


async def get_by_id(db: AsyncSession, goal_id: int) -> Optional[Goal]:
    result = await db.execute(select(Goal).where(Goal.id == goal_id))
    return result.scalar_one_or_none()


async def get_by_group(db: AsyncSession, group_id: int) -> List[Goal]:
    result = await db.execute(select(Goal).where(Goal.creator_id == group_id))
    return list(result.scalars().all())


async def create(db: AsyncSession, data: GoalCreate) -> Goal:
    goal = Goal(
        name=data.name,
        points=data.points,
        deadline=data.deadline,
        creator_id=data.group_id,
    )
    db.add(goal)
    await db.commit()
    await db.refresh(goal)
    return goal


async def update_goal(db: AsyncSession, goal: Goal, data: GoalUpdate) -> Goal:
    if data.name is not None:
        goal.name = data.name
    if data.points is not None:
        goal.points = data.points
    if data.deadline is not None:
        goal.deadline = data.deadline
    await db.commit()
    await db.refresh(goal)
    return goal


async def set_completed(db: AsyncSession, goal: Goal, completed: bool) -> Goal:
    goal.completed = completed
    await db.commit()
    await db.refresh(goal)
    return goal


async def delete(db: AsyncSession, goal: Goal) -> None:
    await db.delete(goal)
    await db.commit()
