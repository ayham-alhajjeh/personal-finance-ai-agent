from sqlalchemy import Column, Integer, String, Date, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

class TransactionDB(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key = True, index = True)
    user_id = Column(Integer, ForeignKey("users.id"), index = True, nullable = False)
    date = Column(Date, nullable = False)
    description = Column(String, nullable = False)
    amount = Column(Numeric(10, 2), nullable = False)
    category_id = Column(Integer, nullable = True)
    
    user = relationship("UserDB", back_populates = "transactions")