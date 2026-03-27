from typing import Optional, List
from sqlalchemy import select, exists, and_, false, update
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.groups.models.group import Group
from app.modules.taxonomy.models.tag import Tag
from app.modules.identity.models.user import User
from app.modules.identity.models.student import Student
from app.modules.identity.models.teacher import Teacher
from app.modules.identity.models.admin import Admin
from app.db.associations import group_teacher_table, group_student_table
from app.modules.groups.schemas.group import GroupCreate, GroupUpdate


# ------------------------------------------------------------------ load options

def _detail_options() -> list:
    return [
        selectinload(Group.teachers).selectinload(Teacher.user),
        selectinload(Group.students).selectinload(Student.user),
        selectinload(Group.tags).selectinload(Tag.category),
        selectinload(Group.administrator),
    ]


# ------------------------------------------------------------------ queries

async def get_by_id(db: AsyncSession, group_id: int) -> Optional[Group]:
    result = await db.execute(select(Group).where(Group.id == group_id))
    return result.scalar_one_or_none()


async def get_by_id_with_details(db: AsyncSession, group_id: int) -> Optional[Group]:
    result = await db.execute(
        select(Group).where(Group.id == group_id).options(*_detail_options())
    )
    return result.scalar_one_or_none()


async def get_all(db: AsyncSession, skip: int = 0, limit: int = 50) -> List[Group]:
    result = await db.execute(select(Group).offset(skip).limit(limit))
    return list(result.scalars().all())


async def get_by_tag(
    db: AsyncSession, tag_id: int, skip: int = 0, limit: int = 50
) -> List[Group]:
    result = await db.execute(
        select(Group)
        .where(Group.tags.any(Tag.id == tag_id))
        .distinct()
        .offset(skip)
        .limit(limit)
    )
    return list(result.scalars().all())


async def get_by_category(
    db: AsyncSession, category_id: int, skip: int = 0, limit: int = 50
) -> List[Group]:
    result = await db.execute(
        select(Group)
        .where(Group.tags.any(Tag.category_id == category_id))
        .distinct()
        .offset(skip)
        .limit(limit)
    )
    return list(result.scalars().all())


async def get_recommended(db: AsyncSession, tag_ids: List[int]) -> List[Group]:
    if not tag_ids:
        return []
    result = await db.execute(
        select(Group)
        .where(Group.tags.any(Tag.id.in_(tag_ids)))
        .distinct()
        .limit(50)
    )
    return list(result.scalars().all())


async def get_user_groups(db: AsyncSession, user: User) -> List[Group]:
    """Return all groups the user belongs to (as student, teacher, or admin).

    Queries the database directly — does not rely on pre-loaded relationships.
    """
    group_ids: set[int] = set()

    if user.student_profile:
        s_result = await db.execute(
            select(Group.id).where(
                Group.students.any(Student.id == user.student_profile.id)
            )
        )
        group_ids.update(s_result.scalars().all())

    if user.teacher_profile:
        t_result = await db.execute(
            select(Group.id).where(
                Group.teachers.any(Teacher.id == user.teacher_profile.id)
            )
        )
        group_ids.update(t_result.scalars().all())

    if user.admin_profile:
        a_result = await db.execute(
            select(Group.id).where(Group.administrator_id == user.admin_profile.id)
        )
        group_ids.update(a_result.scalars().all())

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
    result = await db.execute(
        select(Group).where(Group.id == group.id).options(*_detail_options())
    )
    return result.scalar_one()


async def update_group(db: AsyncSession, group: Group, data: GroupUpdate) -> Group:
    scalar_updates: dict = {}
    if data.name is not None:
        scalar_updates["name"] = data.name
    if data.info is not None:
        scalar_updates["info"] = data.info
    if data.required_teachers is not None:
        scalar_updates["required_teachers"] = data.required_teachers
    if data.required_students is not None:
        scalar_updates["required_students"] = data.required_students

    if scalar_updates:
        await db.execute(
            update(Group).where(Group.id == group.id).values(**scalar_updates)
        )

    if data.tag_ids is not None:
        tags_result = await db.execute(select(Tag).where(Tag.id.in_(data.tag_ids)))
        group.tags = list(tags_result.scalars().all())

    await db.commit()
    result = await db.execute(
        select(Group).where(Group.id == group.id).options(*_detail_options())
    )
    return result.scalar_one()


async def delete(db: AsyncSession, group: Group) -> None:
    await db.delete(group)
    await db.commit()


async def get_user_role_in_group(
    db: AsyncSession, group: Group, user: User
) -> Optional[str]:
    if user.admin_profile and group.administrator_id == user.admin_profile.id:
        return "admin"

    teacher_id = user.teacher_profile.id if user.teacher_profile else None
    student_id = user.student_profile.id if user.student_profile else None

    if teacher_id is None and student_id is None:
        return None

    is_teacher_expr = (
        exists().where(
            and_(
                group_teacher_table.c.group_id == group.id,
                group_teacher_table.c.teacher_id == teacher_id,
            )
        )
        if teacher_id is not None
        else false()
    )
    is_student_expr = (
        exists().where(
            and_(
                group_student_table.c.group_id == group.id,
                group_student_table.c.student_id == student_id,
            )
        )
        if student_id is not None
        else false()
    )

    row = (await db.execute(select(is_teacher_expr, is_student_expr))).one()
    if row[0]:
        return "teacher"
    if row[1]:
        return "student"
    return None


async def add_teacher(db: AsyncSession, group: Group, teacher: Teacher) -> None:
    result = await db.execute(
        select(Group).where(Group.id == group.id).options(selectinload(Group.teachers))
    )
    loaded = result.scalar_one()
    if not any(t.id == teacher.id for t in loaded.teachers):
        loaded.teachers.append(teacher)


async def add_student(db: AsyncSession, group: Group, student: Student) -> None:
    result = await db.execute(
        select(Group).where(Group.id == group.id).options(selectinload(Group.students))
    )
    loaded = result.scalar_one()
    if not any(s.id == student.id for s in loaded.students):
        loaded.students.append(student)


async def remove_teacher(db: AsyncSession, group: Group, teacher: Teacher) -> None:
    result = await db.execute(
        select(Group).where(Group.id == group.id).options(selectinload(Group.teachers))
    )
    loaded = result.scalar_one()
    loaded.teachers = [t for t in loaded.teachers if t.id != teacher.id]


async def remove_student(db: AsyncSession, group: Group, student: Student) -> None:
    result = await db.execute(
        select(Group).where(Group.id == group.id).options(selectinload(Group.students))
    )
    loaded = result.scalar_one()
    loaded.students = [s for s in loaded.students if s.id != student.id]
