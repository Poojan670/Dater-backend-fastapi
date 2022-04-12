import uuid
from database import Base
from sqlalchemy import (Column, ForeignKey,
                        Integer, String,
                        Text, Date, DateTime,
                        Sequence, MetaData, Float,
                        Boolean)
from sqlalchemy.orm import relationship
import sqlalchemy.types as types
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.sql import func

metadata = MetaData()


class ChoiceType(types.TypeDecorator):

    impl = types.String

    def __init__(self, choices, **kw):
        self.choices = dict(choices)
        super(ChoiceType, self).__init__(**kw)

    def process_result_value(self, value, dialect):
        return self.choices[value]


class User(Base):

    __tablename__ = 'user'

    id = Column(String(100), primary_key=True)

    email = Column(String(20))

    phone = Column(String(15))

    password = Column(String(100))

    is_phone_verified = Column(Boolean, default=False)

    is_email_verified = Column(Boolean, default=False)

    role = Column(
        ChoiceType({"A": "Admin",
                    "U": "User"}), nullable=False
    )

    friends = Column(ARRAY(String))

    likes_count = Column(Integer, default=0)

    liked_by = Column(ARRAY(String))

    likes = Column(ARRAY(String))

    report_count = Column(Integer, default=0)

    is_suspended = Column(Boolean, default=False)

    suspend_timestamp = Column(DateTime, nullable=True)

    suspended_count = Column(Integer, default=0)

    user_details = relationship("UserDetails", back_populates="user")

    image_user = relationship("ImagesModel", back_populates="user_images")

    location = relationship("UserLocation", back_populates="user_location")

    time_created = Column(DateTime(timezone=True), server_default=func.now())

    time_updated = Column(DateTime(timezone=True), onupdate=func.now())


class UserDetails(Base):

    __tablename__ = 'userdetails'

    id = Column('id', Text, default=lambda: str(
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

    hobbies = Column(String)

    time_created = Column(DateTime(timezone=True), server_default=func.now())

    user_id = Column(String, ForeignKey("user.id"))

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

    id = Column('id', Text, default=lambda: str(
        uuid.uuid4()), primary_key=True)

    image_url = Column(String)

    user_id = Column(String, ForeignKey("user.id"))

    user_images = relationship("User", back_populates="image_user")

    time_created = Column(DateTime(timezone=True), server_default=func.now())

    time_updated = Column(DateTime(timezone=True), onupdate=func.now())


class UserLocation(Base):

    __tablename__ = 'location'

    id = Column(String(100), primary_key=True)

    user_id = Column(String, ForeignKey("user.id"))

    longitude = Column(Float, default=0)

    latitude = Column(Float, default=0)

    location_name = Column(String(30))

    user_location = relationship("User", back_populates="location")


class FriendRequest(Base):

    __tablename__ = 'friendrequest'

    id = Column(String(100), primary_key=True)

    from_user_id = Column(String, ForeignKey("user.id"), nullable=False)

    from_user = relationship("User", foreign_keys=[from_user_id])

    to_user_id = Column(String, ForeignKey("user.id"), nullable=False)

    to_user = relationship("User", foreign_keys=[to_user_id])

    time_created = Column(DateTime(timezone=True), server_default=func.now())


class ReportUser(Base):

    __tablename__ = 'reportuser'

    id = Column(String(100), primary_key=True)

    report_by_id = Column(String, ForeignKey("user.id"), nullable=False)

    report_by = relationship("User", foreign_keys=[report_by_id])

    report_to_id = Column(String, ForeignKey("user.id"), nullable=False)

    report_to = relationship("User", foreign_keys=[report_to_id])

    report_reason = Column(
        ChoiceType({"I": "Inappropiate Photos",
                    "F": "Feels Like Spam",
                    "U": "User is UnderAge",
                    "O": "Other",
                    }), nullable=False
    )

    time_created = Column(DateTime(timezone=True), server_default=func.now())


class LikeModel(Base):

    __tablename__ = 'userlikes'

    id = id = Column('id', Text, default=lambda: str(
        uuid.uuid4()), primary_key=True)

    like = Column(Boolean, default=False)

    liked_by_id = Column(String, ForeignKey("user.id"), nullable=False)

    liked_by = relationship("User", foreign_keys=[liked_by_id])

    liked_to_id = Column(String, ForeignKey("user.id"), nullable=False)

    liked_to = relationship("User", foreign_keys=[liked_to_id])

    time_created = Column(DateTime(timezone=True), server_default=func.now())
