import uuid
from database import Base
from sqlalchemy import Column, ForeignKey, Integer, String, Text, Date, Table, DateTime, Sequence, MetaData, Boolean
from sqlalchemy.orm import relationship

metadata = MetaData()


class User(Base):

    __tablename__ = 'user'

    id = Column(String(100), primary_key=True)

    email = Column(String(20))

    phone = Column(String(15))

    password = Column(String(5))

    is_verified = Column(Boolean, default=False)

    user_details = relationship("UserDetails", back_populates="user")

    image_user = relationship("ImagesModel", back_populates="user_images")


class UserDetails(Base):

    __tablename__ = 'userdetails'

    id = Column('id', Text(length=36), default=lambda: str(
        uuid.uuid4()), primary_key=True)

    first_name = Column(String)

    middle_name = Column(String)

    last_name = Column(String)

    age = Column(Integer)

    birthday = Column(Date)

    gender = Column(String)

    sexuality = Column(String)

    social_media = Column(String)

    passions = Column(String)

    profession = Column(String)

    living_in = Column(String)

    user_id = Column(Integer, ForeignKey("user.id"))

    user = relationship("User", back_populates="user_details")


class OtpModel(Base):
    __tablename__ = 'otps'

    id = Column(Integer, Sequence("otp_id_seq"), primary_key=True)

    recipient_id = Column(String(100))

    otp_code = Column(String(6))

    created_on = Column(DateTime)

    expiry_time = Column(DateTime)

    is_expired = Column(Boolean, default=False)

    otp_failed_count = Column(Integer, default=0)

    otp_failed_time = Column(DateTime)


class ImagesModel(Base):

    __tablename__ = 'user_images'

    id = Column('id', Text(length=36), default=lambda: str(
        uuid.uuid4()), primary_key=True)

    image = Column(String)

    user_image_id = Column(Integer, ForeignKey("user.id"))

    user_images = relationship("User", back_populates="image_user")
