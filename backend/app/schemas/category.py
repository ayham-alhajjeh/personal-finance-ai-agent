from typing import Optional
from pydantic import BaseModel
from datetime import date

class CategoryBase(BaseModel):
    name: str
    type: Optional[str] = None

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None


class CategoryOut(CategoryBase):
    id: int
    user_id: int
    created_at: date

    class Config:
        orm_mode = True