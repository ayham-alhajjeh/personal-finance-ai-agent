from pydantic import BaseModel
from typing import Optional
from datetime import date

class BudgetBase(BaseModel):
    name: Optional[str] = None
    end_date: date

class BudgetCreate(BudgetBase):
    start_date: Optional[date] = None

class BudgetUpdate(BaseModel):
    name: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None

class BudgetOut(BudgetBase):
    id: int
    user_id: int
    start_date: date

    class Config:
        orm_mode = True