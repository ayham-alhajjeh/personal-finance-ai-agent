from typing import Optional
from pydantic import BaseModel
from datetime import date

class TransactionBase(BaseModel):
    date: date
    description: str
    amount: float
    category_id: Optional[int] = None

class TransactionCreate(TransactionBase):
    pass

class TransactionUpdate(BaseModel):
    date: Optional[date] = None
    description: Optional[str] = None
    amount: Optional[float] = None
    category_id: Optional[int] = None

class TransactionOut(TransactionBase):
    id: int

    class Config:
        orm_mode = True