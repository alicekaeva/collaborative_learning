from typing import TYPE_CHECKING, List
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, IDMixin

if TYPE_CHECKING:
    from app.modules.taxonomy.models.tag import Tag


class Category(IDMixin, Base):
    __tablename__ = "categories"

    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)

    tags: Mapped[List["Tag"]] = relationship("Tag", back_populates="category", lazy="selectin")
