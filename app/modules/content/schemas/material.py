from typing import Optional
from pydantic import BaseModel

from app.modules.identity.schemas.user import UserShort


class MaterialBase(BaseModel):
    name: str
    is_private: bool = False


class MaterialUpdate(BaseModel):
    name: Optional[str] = None
    is_private: Optional[bool] = None


class MaterialRead(MaterialBase):
    id: int
    file_link: str
    mime_type: str
    creator_user_id: Optional[int] = None
    creator_group_id: Optional[int] = None
    creator_user: Optional[UserShort] = None

    model_config = {"from_attributes": True}
