from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, field_validator
from app.schemas.tag import TagRead
from app.schemas.user import UserShort


class PostBase(BaseModel):
    content: str

    @field_validator("content")
    @classmethod
    def content_length(cls, v: str) -> str:
        if len(v) > 500:
            raise ValueError("Содержимое поста не может превышать 500 символов")
        return v


class PostCreate(PostBase):
    tag_ids: List[int] = []


class PostUpdate(BaseModel):
    content: Optional[str] = None
    tag_ids: Optional[List[int]] = None


class PostRead(PostBase):
    id: int
    posting_date: datetime
    author: UserShort
    tags: List[TagRead] = []

    model_config = {"from_attributes": True}
