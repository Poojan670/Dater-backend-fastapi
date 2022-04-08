import uuid
from .database import Base
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text, Table, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


class ImageWelcomeModel(Base):

    __tablename__ = 'image'

    id = Column('id', Text(length=36), default=lambda: str(
        uuid.uuid4()), primary_key=True)

    title = Column(String(20))

    description = Column(String(60))

    image_url = Column(String(100))

    time_created = Column(DateTime(timezone=True), server_default=func.now())

    time_updated = Column(DateTime(timezone=True), onupdate=func.now())


class WelcomeModel(Base):
    __tablename__ = 'welcome'

    id = Column('id', Text(length=36), default=lambda: str(
        uuid.uuid4()), primary_key=True)

    imgid = Column(Integer, ForeignKey('image.id'))

    sub_title = Column(String(20))

    sub_description = Column(String(60))

    image_welcome = relationship("ImageWelcomeModel", back_populates="welcome")

    time_created = Column(DateTime(timezone=True), server_default=func.now())

    time_updated = Column(DateTime(timezone=True), onupdate=func.now())


ImageWelcomeModel.welcome = relationship(
    "WelcomeModel", order_by=WelcomeModel.id, back_populates="image_welcome")
