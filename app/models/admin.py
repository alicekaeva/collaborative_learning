from typing import TYPE_CHECKING, List
from sqlalchemy import Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, IDMixin

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.group import Group


class Admin(IDMixin, Base):
    __tablename__ = "admins"

    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False
    )

    user: Mapped["User"] = relationship("User", back_populates="admin_profile", lazy="selectin")
    managed_groups: Mapped[List["Group"]] = relationship(
        "Group", back_populates="administrator", lazy="noload"
    )
