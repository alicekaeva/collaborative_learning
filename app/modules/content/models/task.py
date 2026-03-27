from datetime import date
from typing import TYPE_CHECKING, Optional
from sqlalchemy import String, Integer, ForeignKey, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, IDMixin

if TYPE_CHECKING:
    from app.modules.groups.models.group import Group


class Task(IDMixin, Base):
    __tablename__ = "tasks"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    link: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    deadline: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    points: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    creator_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("groups.id", ondelete="CASCADE"), nullable=False
    )

    creator: Mapped["Group"] = relationship("Group", back_populates="tasks", lazy="selectin")
