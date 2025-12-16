from sqlalchemy import Column, Integer, String, ForeignKey, Date
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from db.database import Base


class CategoriesDB(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key = True, index = True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable = False)
    name = Column(String, nullable = False)
    type = Column(String, nullable = True)
    created_at = Column(Date, server_default = func.current_date())



    user = relationship("UserDB", back_populates = "categories")
    transactions = relationship("TransactionDB", back_populates = "category")