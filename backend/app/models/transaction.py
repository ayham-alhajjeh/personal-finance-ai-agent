from sqlalchemy import Column, Integer, String, Date, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from db.database import Base

class TransactionDB(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key = True, index = True)
    user_id = Column(Integer, ForeignKey("users.id"), index = True, nullable = False)
    date = Column(Date, nullable = False)
    description = Column(String, nullable = False)
    amount = Column(Numeric(10, 2), nullable = False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable = True)
    
    user = relationship("UserDB", back_populates = "transactions")
    category = relationship("CategoriesDB", back_populates = "transactions")