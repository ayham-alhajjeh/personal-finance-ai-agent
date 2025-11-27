from typing import Optional
from pydantic import BaseModel
from datetime import date

class TransactionBase(BaseModel):
    date: date
    source: str
    description: Optional[str] = None
    amount: float
    category_id: int

class TransactionCreate(TransactionBase):
    pass

class TransactionUpdate(BaseModel):
    date: Optional[date] = None
    source: Optional[str] = None
    description: Optional[str] = None
    amount: Optional[float] = None
    category_id: Optional[int] = None

class TransactionOut(TransactionBase):
    id: int

    class Config:
        orm_mode = True