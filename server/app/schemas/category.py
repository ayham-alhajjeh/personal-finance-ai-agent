from typing import Optional
from pydantic import BaseModel

class CategoryBase(BaseModel):
    name: str
    type: str

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None


class CategoryOut(CategoryBase):
    id: int

    class Config:
        orm_mode = True