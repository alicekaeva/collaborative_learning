from typing import List
from pydantic import BaseModel


class CategoryBase(BaseModel):
    name: str


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: str


class CategoryRead(CategoryBase):
    id: int

    model_config = {"from_attributes": True}
