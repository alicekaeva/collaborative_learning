from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import String, Integer, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, IDMixin
from app.models.associations import group_tag_table, group_teacher_table, group_student_table

if TYPE_CHECKING:
    from app.models.admin import Admin
    from app.models.teacher import Teacher
    from app.models.student import Student
    from app.models.tag import Tag
    from app.models.goal import Goal
    from app.models.task import Task
    from app.models.meeting import Meeting
    from app.models.material import Material
    from app.models.message import Message


class Group(IDMixin, Base):
    __tablename__ = "groups"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    info: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    required_teachers: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    required_students: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    administrator_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("admins.id", ondelete="SET NULL"), nullable=True
    )

    administrator: Mapped[Optional["Admin"]] = relationship(
        "Admin", back_populates="managed_groups", lazy="selectin"
    )
    teachers: Mapped[List["Teacher"]] = relationship(
        "Teacher", secondary=group_teacher_table, back_populates="groups", lazy="selectin"
    )
    students: Mapped[List["Student"]] = relationship(
        "Student", secondary=group_student_table, back_populates="groups", lazy="selectin"
    )
    tags: Mapped[List["Tag"]] = relationship(
        "Tag", secondary=group_tag_table, back_populates="groups", lazy="selectin"
    )
    goals: Mapped[List["Goal"]] = relationship(
        "Goal", back_populates="creator", lazy="noload", cascade="all, delete-orphan"
    )
    tasks: Mapped[List["Task"]] = relationship(
        "Task", back_populates="creator", lazy="noload", cascade="all, delete-orphan"
    )
    meetings: Mapped[List["Meeting"]] = relationship(
        "Meeting", back_populates="creator", lazy="noload", cascade="all, delete-orphan"
    )
    materials: Mapped[List["Material"]] = relationship(
        "Material", back_populates="creator_group", lazy="noload"
    )
    messages: Mapped[List["Message"]] = relationship(
        "Message", back_populates="receiving_group", lazy="noload"
    )
