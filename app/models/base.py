from sqlalchemy.orm import DeclarativeBase, MappedColumn, mapped_column
from sqlalchemy import Integer


class Base(DeclarativeBase):
    pass


class IDMixin:
    id: MappedColumn[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
