from datetime import datetime
from typing import TYPE_CHECKING, Optional
from sqlalchemy import Text, Integer, ForeignKey, Boolean, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, IDMixin

if TYPE_CHECKING:
    from app.modules.identity.models.user import User
    from app.modules.groups.models.group import Group


class Message(IDMixin, Base):
    __tablename__ = "messages"

    content: Mapped[str] = mapped_column(Text, nullable=False)
    is_pinned: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    sending_date: Mapped[datetime] = mapped_column(default=func.now(), nullable=False)
    sender_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    receiver_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True
    )
    receiving_group_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("groups.id", ondelete="CASCADE"), nullable=True
    )

    sender: Mapped["User"] = relationship(
        "User", back_populates="sent_messages", foreign_keys=[sender_id], lazy="selectin"
    )
    receiver: Mapped[Optional["User"]] = relationship(
        "User", back_populates="received_messages", foreign_keys=[receiver_id], lazy="selectin"
    )
    receiving_group: Mapped[Optional["Group"]] = relationship(
        "Group", back_populates="messages", lazy="selectin"
    )
