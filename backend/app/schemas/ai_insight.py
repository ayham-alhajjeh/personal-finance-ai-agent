from pydantic import BaseModel
from datetime import datetime

class AI_InsightBase(BaseModel):
    userID: int
    generatedAt: datetime
    Type: str

class AI_InsightCreate(AI_InsightBase):
    inputContext: str

class AI_InsightOut(AI_InsightBase):
    id: int
    insightText: str

    class Config():
        from_attributes = True