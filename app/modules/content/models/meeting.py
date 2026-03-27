from datetime import datetime
from typing import TYPE_CHECKING, Optional
from sqlalchemy import String, Integer, ForeignKey, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, IDMixin

if TYPE_CHECKING:
    from app.modules.groups.models.group import Group


class Meeting(IDMixin, Base):
    __tablename__ = "meetings"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    agenda: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    link: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    held_on: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    creator_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("groups.id", ondelete="CASCADE"), nullable=False
    )

    creator: Mapped["Group"] = relationship("Group", back_populates="meetings", lazy="selectin")
