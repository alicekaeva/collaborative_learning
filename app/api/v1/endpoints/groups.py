from typing import List, Optional
from fastapi import APIRouter, Depends

from app.api.deps import DBDep, CurrentUser, GroupServiceDep, require_roles
from app.models.user import User
from app.core.exceptions import NotFoundError
from app.crud import group as group_crud
from app.schemas.group import (
    GroupCreate, GroupUpdate, GroupRead, GroupDetail,
    AddGroupMemberRequest, EnrollRequest, UserGroupRole,
)
from app.schemas.common import Message

router = APIRouter(prefix="/groups", tags=["groups"])


@router.get("/", response_model=List[GroupRead])
async def list_groups(
    db: DBDep,
    tag_id: Optional[int] = None,
    category_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 50,
):
    if tag_id:
        return await group_crud.get_by_tag(db, tag_id, skip=skip, limit=limit)
    if category_id:
        return await group_crud.get_by_category(db, category_id, skip=skip, limit=limit)
    return await group_crud.get_all(db, skip=skip, limit=limit)


@router.get("/recommended", response_model=List[GroupRead])
async def recommended_groups(service: GroupServiceDep, current_user: CurrentUser):
    return await service.get_recommended(current_user)


@router.get("/my", response_model=List[GroupRead])
async def my_groups(db: DBDep, current_user: CurrentUser):
    return await group_crud.get_user_groups(db, current_user)


@router.post("/", response_model=GroupDetail, status_code=201)
async def create_group(
    data: GroupCreate,
    service: GroupServiceDep,
    current_user: User = Depends(require_roles("ROLE_ADMIN")),
):
    group = await service.create_group(data, current_user)
    return GroupDetail.model_validate(group)


@router.get("/{group_id}", response_model=GroupDetail)
async def get_group(group_id: int, db: DBDep):
    group = await group_crud.get_by_id(db, group_id)
    if not group:
        raise NotFoundError("Группа не найдена")
    return GroupDetail.model_validate(group)


@router.patch("/{group_id}", response_model=GroupDetail)
async def update_group(
    group_id: int, data: GroupUpdate, service: GroupServiceDep, current_user: CurrentUser
):
    group = await service.update_group(group_id, data, current_user)
    return GroupDetail.model_validate(group)


@router.delete("/{group_id}", status_code=204)
async def delete_group(group_id: int, service: GroupServiceDep, current_user: CurrentUser):
    await service.delete_group(group_id, current_user)


@router.get("/{group_id}/user-role", response_model=UserGroupRole)
async def get_user_role(group_id: int, service: GroupServiceDep, current_user: CurrentUser):
    role = await service.get_user_role(group_id, current_user)
    return UserGroupRole(role=role)


@router.post("/{group_id}/enroll", response_model=Message)
async def enroll_request(
    group_id: int, data: EnrollRequest, service: GroupServiceDep, current_user: CurrentUser
):
    return await service.enroll_request(group_id, data.message, current_user)


@router.post("/{group_id}/members", response_model=GroupDetail, status_code=201)
async def add_group_member(
    group_id: int,
    data: AddGroupMemberRequest,
    service: GroupServiceDep,
    _: User = Depends(require_roles("ROLE_ADMIN")),
):
    group = await service.add_member(group_id, data.user_id, data.role)
    return GroupDetail.model_validate(group)


@router.delete("/{group_id}/members/{user_id}", status_code=204)
async def remove_group_member(
    group_id: int,
    user_id: int,
    role: str,
    service: GroupServiceDep,
    _: User = Depends(require_roles("ROLE_ADMIN")),
):
    await service.remove_member(group_id, user_id, role)
