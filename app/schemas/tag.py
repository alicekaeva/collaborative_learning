from typing import Optional, Any
from pydantic import BaseModel, model_validator


class TagBase(BaseModel):
    name: str
    category_id: Optional[int] = None


class TagCreate(TagBase):
    pass


class TagUpdate(BaseModel):
    name: Optional[str] = None
    category_id: Optional[int] = None


class TagRead(TagBase):
    id: int
    category_name: Optional[str] = None

    model_config = {"from_attributes": True}

    @model_validator(mode="before")
    @classmethod
    def extract_category_name(cls, data: Any) -> Any:
        # When loading from ORM object, extract nested category.name
        if not isinstance(data, dict) and hasattr(data, "__tablename__"):
            category = getattr(data, "category", None)
            return {
                "id": data.id,
                "name": data.name,
                "category_id": data.category_id,
                "category_name": category.name if category else None,
            }
        return data
