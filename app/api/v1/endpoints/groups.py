from typing import List, Optional
from sqlalchemy import select
from fastapi import APIRouter, Depends

from app.api.deps import DBDep, CurrentUser, require_roles
from app.models.user import User
from app.core.exceptions import NotFoundError, ForbiddenError, BadRequestError, ConflictError
from app.crud import group as group_crud
from app.crud import user as user_crud
from app.models.student import Student
from app.models.teacher import Teacher
from app.schemas.group import (
    GroupCreate, GroupUpdate, GroupRead, GroupDetail,
    AddUserToGroupRequest, ChangeUserRoleRequest, EnrollRequest, UserGroupRole
)
from app.schemas.common import Message
from app.services.cache import get_cached, set_cached

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
        return await group_crud.get_by_tag(db, tag_id)
    if category_id:
        return await group_crud.get_by_category(db, category_id)
    return await group_crud.get_all(db, skip=skip, limit=limit)


@router.get("/recommended", response_model=List[GroupRead])
async def recommended_groups(db: DBDep, current_user: CurrentUser):
    cache_key = f"groups:recommended:{current_user.id}"
    cached = await get_cached(cache_key)
    if cached:
        return cached

    tag_ids = [t.id for t in current_user.tags]
    groups = await group_crud.get_recommended(db, tag_ids)
    result = [GroupRead.model_validate(g) for g in groups]
    data = [r.model_dump(mode="json") for r in result]
    await set_cached(cache_key, data)
    return result


@router.get("/my", response_model=List[GroupRead])
async def my_groups(db: DBDep, current_user: CurrentUser):
    return await group_crud.get_user_groups(db, current_user)


@router.post("/", response_model=GroupDetail, status_code=201)
async def create_group(
    data: GroupCreate,
    db: DBDep,
    current_user: User = Depends(require_roles("ROLE_ADMIN")),
):
    if not current_user.admin_profile:
        raise ForbiddenError("Профиль администратора не найден")
    return await group_crud.create(db, data, current_user.admin_profile)


@router.get("/{group_id}", response_model=GroupDetail)
async def get_group(group_id: int, db: DBDep):
    group = await group_crud.get_by_id(db, group_id)
    if not group:
        raise NotFoundError("Группа не найдена")
    return _build_group_detail(group)


@router.patch("/{group_id}", response_model=GroupDetail)
async def update_group(group_id: int, data: GroupUpdate, db: DBDep, current_user: CurrentUser):
    group = await group_crud.get_by_id(db, group_id)
    if not group:
        raise NotFoundError("Группа не найдена")
    role = await group_crud.get_user_role_in_group(db, group, current_user)
    if role != "admin" and "ROLE_ADMIN" not in current_user.roles:
        raise ForbiddenError("Только администратор группы может её редактировать")
    return await group_crud.update_group(db, group, data)


@router.delete("/{group_id}", response_model=Message)
async def delete_group(group_id: int, db: DBDep, current_user: CurrentUser):
    group = await group_crud.get_by_id(db, group_id)
    if not group:
        raise NotFoundError("Группа не найдена")
    role = await group_crud.get_user_role_in_group(db, group, current_user)
    if role != "admin" and "ROLE_ADMIN" not in current_user.roles:
        raise ForbiddenError("Только администратор группы может её удалить")
    await group_crud.delete(db, group)
    return Message(detail="Группа удалена")


@router.get("/{group_id}/user-role", response_model=UserGroupRole)
async def get_user_role(group_id: int, db: DBDep, current_user: CurrentUser):
    group = await group_crud.get_by_id(db, group_id)
    if not group:
        raise NotFoundError("Группа не найдена")
    role = await group_crud.get_user_role_in_group(db, group, current_user)
    return UserGroupRole(role=role)


@router.post("/{group_id}/enroll", response_model=Message)
async def enroll_request(group_id: int, data: EnrollRequest, db: DBDep, current_user: CurrentUser):
    from app.crud import message as message_crud
    group = await group_crud.get_by_id(db, group_id)
    if not group:
        raise NotFoundError("Группа не найдена")
    if not group.administrator:
        raise BadRequestError("У группы нет администратора")
    admin_user_id = group.administrator.user_id
    content = data.message or f"Запрос на вступление в группу '{group.name}'"
    await message_crud.send_direct(db, content, current_user.id, admin_user_id)
    return Message(detail="Запрос на вступление отправлен")


@router.post("/add-user", response_model=GroupDetail)
async def add_user_to_group(
    data: AddUserToGroupRequest,
    db: DBDep,
    _: User = Depends(require_roles("ROLE_ADMIN")),
):
    group = await group_crud.get_by_id(db, data.group_id)
    if not group:
        raise NotFoundError("Группа не найдена")
    target_user = await user_crud.get_by_id(db, data.user_id)
    if not target_user:
        raise NotFoundError("Пользователь не найден")

    if data.role == "teacher":
        if not target_user.teacher_profile:
            teacher = Teacher(user_id=target_user.id)
            db.add(teacher)
            await db.commit()
            await db.refresh(teacher)
            await user_crud.add_role(db, target_user, "ROLE_TEACHER")
            await db.refresh(target_user)
        group = await group_crud.add_teacher(db, group, target_user.teacher_profile)
    elif data.role == "student":
        if not target_user.student_profile:
            student = Student(user_id=target_user.id)
            db.add(student)
            await db.commit()
            await db.refresh(student)
            await user_crud.add_role(db, target_user, "ROLE_STUDENT")
            await db.refresh(target_user)
        group = await group_crud.add_student(db, group, target_user.student_profile)
    else:
        raise BadRequestError("Роль должна быть 'teacher' или 'student'")

    await db.refresh(group)
    return _build_group_detail(group)


@router.post("/remove-user", response_model=Message)
async def remove_user_from_group(
    data: AddUserToGroupRequest,
    db: DBDep,
    _: User = Depends(require_roles("ROLE_ADMIN")),
):
    group = await group_crud.get_by_id(db, data.group_id)
    if not group:
        raise NotFoundError("Группа не найдена")
    target_user = await user_crud.get_by_id(db, data.user_id)
    if not target_user:
        raise NotFoundError("Пользователь не найден")

    if data.role == "teacher" and target_user.teacher_profile:
        await group_crud.remove_teacher(db, group, target_user.teacher_profile)
    elif data.role == "student" and target_user.student_profile:
        await group_crud.remove_student(db, group, target_user.student_profile)
    else:
        raise BadRequestError("Некорректная роль или профиль не найден")

    return Message(detail="Пользователь удалён из группы")


def _build_group_detail(group) -> GroupDetail:
    from app.schemas.user import UserShort
    from app.schemas.tag import TagRead

    teachers = [UserShort.model_validate(t.user) for t in group.teachers if t.user]
    students = [UserShort.model_validate(s.user) for s in group.students if s.user]
    tags = [
        TagRead(
            id=t.id,
            name=t.name,
            category_id=t.category_id,
            category_name=t.category.name if t.category else None,
        )
        for t in group.tags
    ]
    return GroupDetail(
        id=group.id,
        name=group.name,
        info=group.info,
        required_teachers=group.required_teachers,
        required_students=group.required_students,
        administrator_id=group.administrator_id,
        tags=tags,
        teachers=teachers,
        students=students,
    )
