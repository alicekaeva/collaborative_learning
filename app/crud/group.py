from typing import Optional, List
from sqlalchemy import select, or_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.group import Group
from app.models.tag import Tag
from app.models.user import User
from app.models.student import Student
from app.models.teacher import Teacher
from app.models.admin import Admin
from app.schemas.group import GroupCreate, GroupUpdate


async def get_by_id(db: AsyncSession, group_id: int) -> Optional[Group]:
    result = await db.execute(select(Group).where(Group.id == group_id))
    return result.scalar_one_or_none()


async def get_all(db: AsyncSession, skip: int = 0, limit: int = 50) -> List[Group]:
    result = await db.execute(select(Group).offset(skip).limit(limit))
    return list(result.scalars().all())


async def get_by_tag(db: AsyncSession, tag_id: int) -> List[Group]:
    result = await db.execute(
        select(Group).where(Group.tags.any(Tag.id == tag_id))
    )
    return list(result.scalars().all())


async def get_by_category(db: AsyncSession, category_id: int) -> List[Group]:
    result = await db.execute(
        select(Group).where(Group.tags.any(Tag.category_id == category_id))
    )
    return list(result.scalars().all())


async def get_recommended(db: AsyncSession, tag_ids: List[int]) -> List[Group]:
    if not tag_ids:
        return []
    result = await db.execute(
        select(Group).where(Group.tags.any(Tag.id.in_(tag_ids))).limit(50)
    )
    return list(result.scalars().all())


async def get_user_groups(db: AsyncSession, user: User) -> List[Group]:
    """Get all groups where user is student, teacher, or admin."""
    group_ids: set[int] = set()

    if user.student_profile:
        for g in user.student_profile.groups:
            group_ids.add(g.id)
    if user.teacher_profile:
        for g in user.teacher_profile.groups:
            group_ids.add(g.id)
    if user.admin_profile:
        result = await db.execute(
            select(Group).where(Group.administrator_id == user.admin_profile.id)
        )
        for g in result.scalars().all():
            group_ids.add(g.id)

    if not group_ids:
        return []
    result = await db.execute(select(Group).where(Group.id.in_(group_ids)))
    return list(result.scalars().all())


async def create(db: AsyncSession, data: GroupCreate, admin: Admin) -> Group:
    tags_result = await db.execute(select(Tag).where(Tag.id.in_(data.tag_ids)))
    tags = list(tags_result.scalars().all())
    group = Group(
        name=data.name,
        info=data.info,
        required_teachers=data.required_teachers,
        required_students=data.required_students,
        administrator_id=admin.id,
        tags=tags,
    )
    db.add(group)
    await db.commit()
    await db.refresh(group)
    return group


async def update_group(db: AsyncSession, group: Group, data: GroupUpdate) -> Group:
    if data.name is not None:
        group.name = data.name
    if data.info is not None:
        group.info = data.info
    if data.required_teachers is not None:
        group.required_teachers = data.required_teachers
    if data.required_students is not None:
        group.required_students = data.required_students
    if data.tag_ids is not None:
        tags_result = await db.execute(select(Tag).where(Tag.id.in_(data.tag_ids)))
        group.tags = list(tags_result.scalars().all())
    await db.commit()
    await db.refresh(group)
    return group


async def delete(db: AsyncSession, group: Group) -> None:
    await db.delete(group)
    await db.commit()


async def get_user_role_in_group(db: AsyncSession, group: Group, user: User) -> Optional[str]:
    if user.admin_profile and group.administrator_id == user.admin_profile.id:
        return "admin"
    if user.teacher_profile:
        result = await db.execute(
            select(Group)
            .where(Group.id == group.id)
            .options(selectinload(Group.teachers))
        )
        g = result.scalar_one_or_none()
        if g and any(t.id == user.teacher_profile.id for t in g.teachers):
            return "teacher"
    if user.student_profile:
        result = await db.execute(
            select(Group)
            .where(Group.id == group.id)
            .options(selectinload(Group.students))
        )
        g = result.scalar_one_or_none()
        if g and any(s.id == user.student_profile.id for s in g.students):
            return "student"
    return None


async def add_teacher(db: AsyncSession, group: Group, teacher: Teacher) -> Group:
    result = await db.execute(
        select(Group).where(Group.id == group.id).options(selectinload(Group.teachers))
    )
    group = result.scalar_one()
    if not any(t.id == teacher.id for t in group.teachers):
        group.teachers.append(teacher)
        await db.commit()
        await db.refresh(group)
    return group


async def add_student(db: AsyncSession, group: Group, student: Student) -> Group:
    result = await db.execute(
        select(Group).where(Group.id == group.id).options(selectinload(Group.students))
    )
    group = result.scalar_one()
    if not any(s.id == student.id for s in group.students):
        group.students.append(student)
        await db.commit()
        await db.refresh(group)
    return group


async def remove_teacher(db: AsyncSession, group: Group, teacher: Teacher) -> None:
    result = await db.execute(
        select(Group).where(Group.id == group.id).options(selectinload(Group.teachers))
    )
    group = result.scalar_one()
    group.teachers = [t for t in group.teachers if t.id != teacher.id]
    await db.commit()


async def remove_student(db: AsyncSession, group: Group, student: Student) -> None:
    result = await db.execute(
        select(Group).where(Group.id == group.id).options(selectinload(Group.students))
    )
    group = result.scalar_one()
    group.students = [s for s in group.students if s.id != student.id]
    await db.commit()
