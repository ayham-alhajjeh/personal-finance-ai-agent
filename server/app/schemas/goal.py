from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from datetime import date

class GoalsBase(BaseModel):
    userID: int
    created_at: datetime

class GoalsCreate(GoalsBase):
    name: str
    targetAmount: Optional[float]
    targetDate: Optional[date]

class GoalsUpdate(GoalsBase):
    name: Optional[str]: None
    targetAmount: Optional[float] = None
    targetDate: Optional[date] = None

class GoalsOut(GoalsBase):
    id: int

    class Config():
        orm_mode = True