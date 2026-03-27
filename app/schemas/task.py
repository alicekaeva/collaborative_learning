from datetime import date
from typing import Optional
from pydantic import BaseModel


class TaskBase(BaseModel):
    name: str
    link: Optional[str] = None
    deadline: Optional[date] = None
    points: int = 0


class TaskCreate(TaskBase):
    group_id: int


class TaskUpdate(BaseModel):
    name: Optional[str] = None
    link: Optional[str] = None
    deadline: Optional[date] = None
    points: Optional[int] = None


class TaskRead(TaskBase):
    id: int
    creator_id: int

    model_config = {"from_attributes": True}
