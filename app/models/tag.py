from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, IDMixin

if TYPE_CHECKING:
    from app.models.category import Category
    from app.models.user import User
    from app.models.post import Post
    from app.models.group import Group


class Tag(IDMixin, Base):
    __tablename__ = "tags"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    category_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True
    )

    category: Mapped[Optional["Category"]] = relationship("Category", back_populates="tags", lazy="selectin")
    users: Mapped[List["User"]] = relationship(
        "User", secondary="user_tag", back_populates="tags", lazy="noload"
    )
    posts: Mapped[List["Post"]] = relationship(
        "Post", secondary="post_tag", back_populates="tags", lazy="noload"
    )
    groups: Mapped[List["Group"]] = relationship(
        "Group", secondary="group_tag", back_populates="tags", lazy="noload"
    )
