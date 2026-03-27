from typing import TYPE_CHECKING, Optional
from sqlalchemy import String, Integer, ForeignKey, Boolean, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, IDMixin

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.group import Group


class Material(IDMixin, Base):
    __tablename__ = "materials"
    __table_args__ = (
        CheckConstraint(
            "(creator_user_id IS NOT NULL AND creator_group_id IS NULL)"
            " OR (creator_user_id IS NULL AND creator_group_id IS NOT NULL)",
            name="ck_material_exactly_one_creator",
        ),
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_link: Mapped[str] = mapped_column(String(500), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    is_private: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    creator_user_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    creator_group_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("groups.id", ondelete="SET NULL"), nullable=True
    )

    creator_user: Mapped[Optional["User"]] = relationship(
        "User", back_populates="materials", lazy="selectin"
    )
    creator_group: Mapped[Optional["Group"]] = relationship(
        "Group", back_populates="materials", lazy="selectin"
    )
