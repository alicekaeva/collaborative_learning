# Alembic + legacy import compatibility — all canonical definitions live in app/modules/
from app.db.base import Base
from app.db.associations import (
    user_tag_table,
    user_favorite_post_table,
    post_tag_table,
    group_tag_table,
    group_teacher_table,
    group_student_table,
)
from app.modules.taxonomy.models.category import Category
from app.modules.taxonomy.models.tag import Tag
from app.modules.identity.models.user import User
from app.modules.identity.models.student import Student
from app.modules.identity.models.teacher import Teacher
from app.modules.identity.models.admin import Admin
from app.modules.groups.models.group import Group
from app.modules.content.models.post import Post
from app.modules.content.models.material import Material
from app.modules.content.models.goal import Goal
from app.modules.content.models.task import Task
from app.modules.content.models.meeting import Meeting
from app.modules.messaging.models.message import Message

__all__ = [
    "Base",
    "user_tag_table",
    "user_favorite_post_table",
    "post_tag_table",
    "group_tag_table",
    "group_teacher_table",
    "group_student_table",
    "Category",
    "Tag",
    "User",
    "Student",
    "Teacher",
    "Admin",
    "Group",
    "Post",
    "Material",
    "Message",
    "Goal",
    "Task",
    "Meeting",
]
