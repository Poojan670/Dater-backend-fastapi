import uuid
from database import Base
from sqlalchemy import Column, String, Text, DateTime
from sqlalchemy.orm import relationship
from pydantic import BaseModel
from sqlalchemy.sql import func


class PremiumBase(BaseModel):
    header: str

    sub_title: str
    sub_description: str
    footer: str
    footer_description: str


class PremiumShowId(BaseModel):
    id: str

    class Config():
        orm_mode = True


class PremiumRetrieve(BaseModel):
    header: str
    img_url: str
    sub_title: str
    sub_description: str
    footer: str
    footer_description: str

    class Config():
        orm_mode = True


class DaterPlusModel(Base):
    __tablename__ = 'dater_plus'

    id = Column('id', Text(length=36), default=lambda: str(
        uuid.uuid4()), primary_key=True)

    header = Column(String(30))

    img_url = Column(String)

    sub_title = Column(String(20))

    sub_description = Column(Text)

    footer = Column(String(30))

    footer_description = Column(Text)

    time_created = Column(DateTime(timezone=True), server_default=func.now())

    time_updated = Column(DateTime(timezone=True), onupdate=func.now())
