import uuid
from database import Base
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text, Table
from sqlalchemy.orm import relationship


class ImageWelcomeModel(Base):

    __tablename__ = 'image'

    id = Column('id', Text(length=36), default=lambda: str(
        uuid.uuid4()), primary_key=True)

    title = Column(String(20))

    description = Column(String(60))

    image_url = Column(String(100))


class WelcomeModel(Base):
    __tablename__ = 'welcome'

    id = Column('id', Text(length=36), default=lambda: str(
        uuid.uuid4()), primary_key=True)

    imgid = Column(Integer, ForeignKey('image.id'))

    sub_title = Column(String(20))

    sub_description = Column(String(60))

    image_welcome = relationship("ImageWelcomeModel", back_populates="welcome")


ImageWelcomeModel.welcome = relationship(
    "WelcomeModel", order_by=WelcomeModel.id, back_populates="image_welcome")
