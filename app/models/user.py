from datetime import datetime
from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import String, Integer, func
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, IDMixin
from app.models.associations import user_tag_table, user_favorite_post_table

if TYPE_CHECKING:
    from app.models.tag import Tag
    from app.models.post import Post
    from app.models.material import Material
    from app.models.message import Message
    from app.models.student import Student
    from app.models.teacher import Teacher
    from app.models.admin import Admin


class User(IDMixin, Base):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    phone_number: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    age: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    alma_mater: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    points_amount: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    roles: Mapped[List[str]] = mapped_column(ARRAY(String), default=list, nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)

    tags: Mapped[List["Tag"]] = relationship(
        "Tag", secondary=user_tag_table, back_populates="users", lazy="selectin"
    )
    favorite_posts: Mapped[List["Post"]] = relationship(
        "Post", secondary=user_favorite_post_table, back_populates="favorited_by", lazy="noload"
    )
    posts: Mapped[List["Post"]] = relationship(
        "Post", back_populates="author", lazy="noload", cascade="all, delete-orphan"
    )
    materials: Mapped[List["Material"]] = relationship(
        "Material", back_populates="creator_user", lazy="noload"
    )
    sent_messages: Mapped[List["Message"]] = relationship(
        "Message", back_populates="sender", foreign_keys="Message.sender_id", lazy="noload"
    )
    received_messages: Mapped[List["Message"]] = relationship(
        "Message", back_populates="receiver", foreign_keys="Message.receiver_id", lazy="noload"
    )

    # noload by default — explicitly loaded via selectinload() in queries that need profiles
    student_profile: Mapped[Optional["Student"]] = relationship(
        "Student", back_populates="user", uselist=False, lazy="noload", cascade="all, delete-orphan"
    )
    teacher_profile: Mapped[Optional["Teacher"]] = relationship(
        "Teacher", back_populates="user", uselist=False, lazy="noload", cascade="all, delete-orphan"
    )
    admin_profile: Mapped[Optional["Admin"]] = relationship(
        "Admin", back_populates="user", uselist=False, lazy="noload", cascade="all, delete-orphan"
    )
