# Backward-compatibility shim — canonical source: app.db.associations
from app.db.associations import (
    user_tag_table,
    user_favorite_post_table,
    post_tag_table,
    group_tag_table,
    group_teacher_table,
    group_student_table,
)

__all__ = [
    "user_tag_table",
    "user_favorite_post_table",
    "post_tag_table",
    "group_tag_table",
    "group_teacher_table",
    "group_student_table",
]
