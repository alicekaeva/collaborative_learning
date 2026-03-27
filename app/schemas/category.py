from typing import Optional, List
from pydantic import BaseModel
from app.schemas.tag import TagRead


class CategoryBase(BaseModel):
    name: str


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = None


class CategoryRead(CategoryBase):
    id: int
    tags: List[TagRead] = []

    model_config = {"from_attributes": True}
