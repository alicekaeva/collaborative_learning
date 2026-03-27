from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field

from app.modules.taxonomy.schemas.tag import TagRead


class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    phone_number: Optional[str] = None
    age: Optional[int] = None
    alma_mater: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    age: Optional[int] = None
    alma_mater: Optional[str] = None
    tag_ids: Optional[List[int]] = None


class UserRead(UserBase):
    id: int
    points_amount: int
    roles: List[str]
    created_at: datetime
    tags: List[TagRead] = []

    model_config = {"from_attributes": True}


class UserShort(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    roles: List[str]
    points_amount: int

    model_config = {"from_attributes": True}


class EarnPointsRequest(BaseModel):
    points: int = Field(gt=0, le=10000)
