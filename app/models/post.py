from datetime import datetime
from typing import TYPE_CHECKING, List
from sqlalchemy import Text, Integer, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, IDMixin
from app.models.associations import post_tag_table, user_favorite_post_table

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.tag import Tag


class Post(IDMixin, Base):
    __tablename__ = "posts"

    content: Mapped[str] = mapped_column(Text, nullable=False)
    posting_date: Mapped[datetime] = mapped_column(default=func.now(), nullable=False)
    author_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    author: Mapped["User"] = relationship("User", back_populates="posts", lazy="selectin")
    tags: Mapped[List["Tag"]] = relationship(
        "Tag", secondary=post_tag_table, back_populates="posts", lazy="selectin"
    )
    favorited_by: Mapped[List["User"]] = relationship(
        "User", secondary=user_favorite_post_table, back_populates="favorite_posts", lazy="noload"
    )
