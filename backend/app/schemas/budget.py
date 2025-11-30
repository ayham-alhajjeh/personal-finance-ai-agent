from pydantic import BaseModel
from typing import Optional
from datetime import date
from datetime import datetime

class BudgetBase(BaseModel):
    userID: int
    

class BudgetCreate(BudgetBase):
    name: str
    start_date: Optional[date]
    end_date: Optional[date]
    created_at: datetime

class BudgetUpdate(BudgetBase):
    name: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date]


class BudgetOut(BudgetBase):
    id: int

    class Config():
        orm_mode = True