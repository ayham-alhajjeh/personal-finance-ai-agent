from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date

class GoalsBase(BaseModel):
    name: str
    target_amount: Optional[int] = None
    target_date: Optional[date] = None

class GoalsCreate(GoalsBase):
    pass

class GoalsUpdate(BaseModel):
    name: Optional[str] = None
    target_amount: Optional[int] = None
    target_date: Optional[date] = None

class GoalsOut(GoalsBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        orm_mode = True