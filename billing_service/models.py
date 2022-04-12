import uuid
from database import Base
from sqlalchemy import Column, ForeignKey, String, Text, DateTime, Integer, Boolean, Date
from sqlalchemy.orm import relationship
from pydantic import BaseModel
from sqlalchemy.sql import func
from datetime import date
from typing import List


class UserRetrieve(BaseModel):
    id: str
    is_expired: bool
    bill: str
    user_id: str
    date_created: date


class ShowUserId(BaseModel):
    id: str
    
    class Config():
        orm_mode= True

class ShowBilling(BaseModel):
    user: List[UserRetrieve] = []
    
    class Config():
        orm_mode=True
    
class BillingModel(Base):

    __tablename__ = 'billing'

    id = Column('id', Text, default=lambda: str(
        uuid.uuid4()), primary_key=True)

    subscription_time_months = Column(Integer, default=6)

    price = Column(Integer, default=10)

    time_created = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("UserModel", back_populates="billing")


class UserModel(Base):

    __tablename__ = 'userBilling'

    id = Column('id', Text, default=lambda: str(
        uuid.uuid4()), primary_key=True)

    is_expired = Column(Boolean, default=False)

    bill = Column(String, ForeignKey("billing.id"), nullable=False)

    user_id = Column(String)

    date_created = Column(Date, server_default=func.now())

    billing = relationship("BillingModel", back_populates="user")
