from typing import Optional, List
from pydantic import BaseModel
from app.schemas.tag import TagRead
from app.schemas.user import UserShort


class GroupBase(BaseModel):
    name: str
    info: Optional[str] = None
    required_teachers: int = 1
    required_students: int = 1


class GroupCreate(GroupBase):
    tag_ids: List[int] = []


class GroupUpdate(BaseModel):
    name: Optional[str] = None
    info: Optional[str] = None
    required_teachers: Optional[int] = None
    required_students: Optional[int] = None
    tag_ids: Optional[List[int]] = None


class GroupRead(GroupBase):
    id: int
    tags: List[TagRead] = []
    administrator_id: Optional[int] = None

    model_config = {"from_attributes": True}


class GroupDetail(GroupRead):
    teachers: List[UserShort] = []
    students: List[UserShort] = []


class AddUserToGroupRequest(BaseModel):
    group_id: int
    user_id: int
    role: str  # "teacher" | "student"


class ChangeUserRoleRequest(BaseModel):
    group_id: int
    user_id: int
    new_role: str  # "teacher" | "student"


class EnrollRequest(BaseModel):
    group_id: int
    message: Optional[str] = None


class UserGroupRole(BaseModel):
    role: Optional[str]  # "teacher" | "student" | "admin" | None
