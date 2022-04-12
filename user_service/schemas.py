from datetime import date
from pydantic import BaseModel, constr, EmailStr, validator, Field, FilePath
from typing import Optional, List
from pydantic_choices import choice
import re


class Settings(BaseModel):
    authjwt_secret_key: str = "asdifhjoih124n12fndsk215sdafadf"


gender_choices = choice(["male",
                         "female",
                         "non-binary",
                         "transgender"
                         "transgender female"
                         "transgender male"])

sexuality_choices = choice([
    "Straight",
    "Homosexual",
    "Bisexual",
    "Asexual",
])

social_media_choices = choice([
    "GOOGLE",
    "Facebook",
    "Instagram",
])


class UserDetailsBase(BaseModel):
    first_name: constr(min_length=2, max_length=15)
    middle_name: str
    last_name: constr(min_length=5, max_length=15)
    age: int

    birthday: date

    gender: gender_choices

    sexuality: sexuality_choices

    social_media: social_media_choices

    passions: str

    profession: str

    hobbies: str


class UserDetails(UserDetailsBase):

    class Config():
        orm_mode = True


class ShowItem(UserDetailsBase):
    id: str
    user_id: str

    class Config:
        orm_mode = True


class ShowUserDetailsBase(UserDetailsBase):
    class Config():
        orm_mode = True


class ShowIdUserDetails(BaseModel):
    id: str

    class Config():
        orm_mode = True


class ImageBase(BaseModel):
    user_id: str


class ImageRetrieve(BaseModel):
    id: str
    image_url: str
    user_id: str

    class Config():
        orm_mode = True


class ShowImageId(BaseModel):
    id: str

    class Config():
        orm_mode = True


class Image(BaseModel):
    id: str
    image_url: str

    class Config():
        orm_mode = True


class LocationBase(BaseModel):
    longitude: float
    latitude: float
    location_name: constr(min_length=3, max_length=100)

    class Config():
        orm_mode = True


class Friends(BaseModel):
    friends: str

    class Config:
        orm_mode = True


class AllLocation(BaseModel):
    id: str

    class Config():
        orm_mode = True


class LocationFilter(BaseModel):
    user_id: str

    class Config():
        orm_mode = True


class ReportBase(BaseModel):
    report_to_id: str
    report_reason: str

    class Config():
        orm_mode = True


class ReportList(BaseModel):
    id: str

    class Config():
        orm_mode = True


class LikesList(BaseModel):
    liked_by: list


class Likes(BaseModel):
    likes: Optional[List[LikesList]] = []

    class Config():
        orm_mode = True


class UserBase(BaseModel):
    role: str
    email: EmailStr
    phone: constr(min_length=10, max_length=15)

    @validator("phone")
    def phone_validation(cls, v):
        regex = r"^(\+)[1-9][0-9\-\(\)\.]{9,15}$"
        if v and not re.search(regex, v, re.I):
            raise ValueError("Phone Number Invalid.")
        return v
    password: str = Field(..., example="password123")


class UserPhoneBase(BaseModel):
    phone: constr(min_length=10, max_length=15)

    @validator("phone")
    def phone_validation(cls, v):
        regex = r"^(\+)[1-9][0-9\-\(\)\.]{9,15}$"
        if v and not re.search(regex, v, re.I):
            raise ValueError("Phone Number Invalid.")
        return v
    password: str = Field(..., example="password123")


class UserEmailBase(BaseModel):
    email: EmailStr


class UserEmail(UserEmailBase):
    class Config():
        orm_mode = True


class UserPhone(UserPhoneBase):

    class Config():
        orm_mode = True


class User(UserBase):

    class Config():
        orm_mode = True


class UserDetailsFilter(BaseModel):
    user_id: str

    class Config():
        orm_mode = True


class UserLikedFilter(BaseModel):
    likes: Optional[list] = None

    class Config():
        orm_mode = True


class UserAuth(BaseModel):
    email: str
    password: str


class ShowUser(BaseModel):

    id: str
    email: Optional[str] = None
    phone: str

    is_phone_verified: bool
    is_email_verified: bool

    class Config():
        orm_mode = True


class ShowUserDetails(BaseModel):
    user_details: List[ShowUserDetailsBase] = []

    class Config():
        orm_mode = True


class ShowImageList(BaseModel):
    image_user: List[Image] = []

    class Config():
        orm_mode = True


class ShowUserLocation(BaseModel):
    location: List[LocationBase] = []

    class Config():
        orm_mode = True


class ShowFriendsList(BaseModel):
    location: List[LocationBase] = []

    class Config():
        orm_mode = True


class ShowIdUser(BaseModel):
    id: str

    class Config():
        orm_mode = True


class Login(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: Optional[str] = None


class TokenData(BaseModel):
    phone: str


class CreateOTP(BaseModel):
    recipient_id: str


class VerifyOTP(BaseModel):
    otp_code: str


class OTPList(VerifyOTP):
    otp_failed_count: str


class DeleteFriends(BaseModel):
    friend_id: str
