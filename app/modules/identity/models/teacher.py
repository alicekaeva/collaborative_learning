from typing import TYPE_CHECKING, List
from sqlalchemy import Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, IDMixin
from app.db.associations import group_teacher_table

if TYPE_CHECKING:
    from app.modules.identity.models.user import User
    from app.modules.groups.models.group import Group


class Teacher(IDMixin, Base):
    __tablename__ = "teachers"

    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False
    )

    user: Mapped["User"] = relationship("User", back_populates="teacher_profile", lazy="selectin")
    groups: Mapped[List["Group"]] = relationship(
        "Group", secondary=group_teacher_table, back_populates="teachers", lazy="selectin"
    )
