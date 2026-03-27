from typing import Any, Optional, List
from pydantic import BaseModel, model_validator
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

    @model_validator(mode="before")
    @classmethod
    def extract_members(cls, data: Any) -> Any:
        """
        Handles ORM objects with teacher/student profiles.
        Extracts User from each profile so Pydantic sees List[User] for teachers/students.
        """
        if not hasattr(data, "teachers"):
            return data
        return {
            "id": data.id,
            "name": data.name,
            "info": data.info,
            "required_teachers": data.required_teachers,
            "required_students": data.required_students,
            "administrator_id": data.administrator_id,
            "tags": list(data.tags),
            "teachers": [t.user for t in data.teachers if t.user],
            "students": [s.user for s in data.students if s.user],
        }


class AddUserToGroupRequest(BaseModel):
    group_id: int
    user_id: int
    role: str  # "teacher" | "student"


class AddGroupMemberRequest(BaseModel):
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
