from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError, ForbiddenError, BadRequestError
from app.crud import group as group_crud
from app.crud import user as user_crud
from app.models.user import User
from app.models.group import Group
from app.models.student import Student
from app.models.teacher import Teacher
from app.schemas.group import GroupCreate, GroupUpdate, GroupRead
from app.schemas.common import Message
from app.services.cache import get_cached, set_cached


class GroupService:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def create_group(self, data: GroupCreate, current_user: User) -> Group:
        if not current_user.admin_profile:
            raise ForbiddenError("Профиль администратора не найден")
        return await group_crud.create(self._db, data, current_user.admin_profile)

    async def update_group(self, group_id: int, data: GroupUpdate, current_user: User) -> Group:
        group = await self._get_or_404(group_id)
        role = await group_crud.get_user_role_in_group(self._db, group, current_user)
        if role != "admin" and "ROLE_ADMIN" not in current_user.roles:
            raise ForbiddenError("Только администратор группы может её редактировать")
        return await group_crud.update_group(self._db, group, data)

    async def delete_group(self, group_id: int, current_user: User) -> None:
        group = await self._get_or_404(group_id)
        role = await group_crud.get_user_role_in_group(self._db, group, current_user)
        if role != "admin" and "ROLE_ADMIN" not in current_user.roles:
            raise ForbiddenError("Только администратор группы может её удалить")
        await group_crud.delete(self._db, group)

    async def add_member(self, group_id: int, user_id: int, role: str) -> Group:
        """
        Atomically creates role profile if absent, assigns system role, and adds to group.
        All writes happen in a single transaction (no intermediate commits).
        """
        group = await self._get_or_404(group_id)
        target_user = await self._get_user_with_profiles(user_id)

        if role == "teacher":
            if not target_user.teacher_profile:
                teacher = Teacher(user_id=target_user.id)
                self._db.add(teacher)
                await self._db.flush()
                # Reload target_user so teacher_profile is visible in this transaction
                target_user = await self._get_user_with_profiles(target_user.id)
            if not target_user.teacher_profile:
                raise BadRequestError("Не удалось создать профиль преподавателя")
            # Assign role in-memory (no commit) so the whole operation is atomic
            if "ROLE_TEACHER" not in target_user.roles:
                target_user.roles = target_user.roles + ["ROLE_TEACHER"]
            await group_crud.add_teacher(self._db, group, target_user.teacher_profile)

        elif role == "student":
            if not target_user.student_profile:
                student = Student(user_id=target_user.id)
                self._db.add(student)
                await self._db.flush()
                target_user = await self._get_user_with_profiles(target_user.id)
            if not target_user.student_profile:
                raise BadRequestError("Не удалось создать профиль студента")
            if "ROLE_STUDENT" not in target_user.roles:
                target_user.roles = target_user.roles + ["ROLE_STUDENT"]
            await group_crud.add_student(self._db, group, target_user.student_profile)

        else:
            raise BadRequestError("Роль должна быть 'teacher' или 'student'")

        # Single commit for the entire operation
        await self._db.commit()
        return await group_crud.get_by_id_with_details(self._db, group_id)

    async def remove_member(self, group_id: int, user_id: int, role: str) -> None:
        group = await self._get_or_404(group_id)
        target_user = await self._get_user_with_profiles(user_id)

        if role == "teacher" and target_user.teacher_profile:
            await group_crud.remove_teacher(self._db, group, target_user.teacher_profile)
            # Check if user is still a teacher in any other group before removing system role
            remaining = await self._db.execute(
                select(Group).where(
                    Group.teachers.any(Teacher.id == target_user.teacher_profile.id)
                )
            )
            if not remaining.scalars().first():
                await user_crud.remove_role(self._db, target_user, "ROLE_TEACHER")
        elif role == "student" and target_user.student_profile:
            await group_crud.remove_student(self._db, group, target_user.student_profile)
            remaining = await self._db.execute(
                select(Group).where(
                    Group.students.any(Student.id == target_user.student_profile.id)
                )
            )
            if not remaining.scalars().first():
                await user_crud.remove_role(self._db, target_user, "ROLE_STUDENT")
        else:
            raise BadRequestError("Некорректная роль или профиль не найден")

    async def enroll_request(
        self, group_id: int, message_text: Optional[str], requester: User
    ) -> Message:
        from app.crud import message as message_crud

        group = await self._get_or_404(group_id)
        if not group.administrator:
            raise BadRequestError("У группы нет администратора")
        admin_user_id = group.administrator.user_id
        content = message_text or f"Запрос на вступление в группу '{group.name}'"
        await message_crud.send_direct(self._db, content, requester.id, admin_user_id)
        return Message(detail="Запрос на вступление отправлен")

    async def get_recommended(self, current_user: User) -> List[GroupRead]:
        cache_key = f"groups:recommended:{current_user.id}"
        cached = await get_cached(cache_key)
        if cached:
            # Deserialize back to GroupRead instances, not raw dicts
            return [GroupRead.model_validate(item) for item in cached]
        tag_ids = [t.id for t in current_user.tags]
        groups = await group_crud.get_recommended(self._db, tag_ids)
        result = [GroupRead.model_validate(g) for g in groups]
        await set_cached(cache_key, [r.model_dump(mode="json") for r in result])
        return result

    async def get_user_role(self, group_id: int, current_user: User) -> Optional[str]:
        group = await self._get_or_404(group_id)
        return await group_crud.get_user_role_in_group(self._db, group, current_user)

    # ------------------------------------------------------------------ helpers

    async def _get_or_404(self, group_id: int) -> Group:
        group = await group_crud.get_by_id(self._db, group_id)
        if not group:
            raise NotFoundError("Группа не найдена")
        return group

    async def _get_user_with_profiles(self, user_id: int) -> User:
        result = await self._db.execute(
            select(User)
            .where(User.id == user_id)
            .options(
                selectinload(User.student_profile),
                selectinload(User.teacher_profile),
            )
        )
        user = result.scalar_one_or_none()
        if not user:
            raise NotFoundError("Пользователь не найден")
        return user
