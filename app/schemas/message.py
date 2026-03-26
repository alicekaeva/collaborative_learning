from datetime import datetime
from typing import Optional
from pydantic import BaseModel, field_validator
from app.schemas.user import UserShort


class MessageBase(BaseModel):
    content: str

    @field_validator("content")
    @classmethod
    def content_length(cls, v: str) -> str:
        if len(v) > 1000:
            raise ValueError("Сообщение не может превышать 1000 символов")
        return v


class SendDirectMessageRequest(MessageBase):
    receiver_id: int


class SendGroupMessageRequest(MessageBase):
    receiving_group_id: int


class MessageRead(MessageBase):
    id: int
    is_pinned: bool
    sending_date: datetime
    sender: UserShort
    receiver_id: Optional[int] = None
    receiving_group_id: Optional[int] = None

    model_config = {"from_attributes": True}


class DialogPreview(BaseModel):
    user: UserShort
    last_message: Optional[str] = None
    last_message_date: Optional[datetime] = None
