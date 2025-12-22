from sqlalchemy import Column, Integer, String, DateTime, Numeric, Boolean, JSON, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from db.database import Base


class UserDB(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key = True, index = True)
    email = Column(String, unique = True, index = True, nullable = False)
    name = Column(String, nullable = True)
    created_at = Column(DateTime(timezone=True), server_default = func.now())
    hashed_password = Column(String, nullable = False)

    
    transactions = relationship("TransactionDB", back_populates = "user")
    categories = relationship("CategoriesDB", back_populates = "user")
    budgets = relationship("BudgetsDB", back_populates = "user")
    goals = relationship("GoalsDB", back_populates = "user")