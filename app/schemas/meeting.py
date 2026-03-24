from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class MeetingBase(BaseModel):
    name: str
    agenda: Optional[str] = None
    link: Optional[str] = None
    held_on: Optional[datetime] = None


class MeetingCreate(MeetingBase):
    group_id: int


class MeetingUpdate(BaseModel):
    name: Optional[str] = None
    agenda: Optional[str] = None
    link: Optional[str] = None
    held_on: Optional[datetime] = None


class MeetingRead(MeetingBase):
    id: int
    creator_id: int

    model_config = {"from_attributes": True}
