from datetime import date
from typing import Optional
from pydantic import BaseModel


class GoalBase(BaseModel):
    name: str
    points: int = 0
    deadline: Optional[date] = None


class GoalCreate(GoalBase):
    group_id: int


class GoalUpdate(BaseModel):
    name: Optional[str] = None
    points: Optional[int] = None
    deadline: Optional[date] = None


class GoalRead(GoalBase):
    id: int
    completed: bool
    creator_id: int

    model_config = {"from_attributes": True}
