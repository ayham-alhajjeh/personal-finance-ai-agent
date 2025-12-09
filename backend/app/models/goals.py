from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey
from sqlalchemy.sql import func
from db.database import Base
from sqlalchemy.orm import relationship

class GoalsDB(Base):
    __tablename__ = "goals"

    id = Column(Integer, primary_key = True, index = True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable = False)
    name = Column(String, nullable = False)
    target_amount = Column(Integer, nullable = True)
    target_date = Column(Date, nullable = True)
    created_at = Column(DateTime(timezone=True), server_default = func.now())


    user = relationship("UserDB", back_populates = "goals")