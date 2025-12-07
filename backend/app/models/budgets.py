from sqlalchemy import Column, String, Integer, ForeignKey, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from db.database import Base

class BudgetsDB(Base):
    __tablename__ = "budgets"

    id = Column(Integer, primary_key = True, index = True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable = False)
    name = Column(String, nullable = True)
    start_date = Column(Date, server_default = func.current_date())
    end_date = Column(Date, nullable = False)

    user = relationship("UserDB", back_populates = "budgets")