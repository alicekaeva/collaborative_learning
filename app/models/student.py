from typing import TYPE_CHECKING, List
from sqlalchemy import Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, IDMixin
from app.models.associations import group_student_table

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.group import Group


class Student(IDMixin, Base):
    __tablename__ = "students"

    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False
    )

    user: Mapped["User"] = relationship("User", back_populates="student_profile", lazy="selectin")
    groups: Mapped[List["Group"]] = relationship(
        "Group", secondary=group_student_table, back_populates="students", lazy="selectin"
    )
