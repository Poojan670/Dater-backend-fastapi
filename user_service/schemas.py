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
    first_name: constr(min_length=5, max_length=15)
    middle_name: str
    last_name: constr(min_length=5, max_length=15)
    age: int

    birthday: date

    gender: gender_choices

    sexuality: sexuality_choices

    social_media: social_media_choices

    passions: str

    profession: str

    living_in: str

    user_id: str


class UserDetails(UserDetailsBase):

    class Config():
        orm_mode = True


class ShowItem(UserDetailsBase):
    id: str
    user_id: str

    class Config:
        orm_mode = True


class ShowIdUserDetails(BaseModel):
    id: str

    class Config():
        orm_mode = True


class ImageBase(BaseModel):
    user_image_id: str


class ImageRetrieve(BaseModel):
    id: str
    image: str
    user_image_id: str

    class Config():
        orm_mode = True


class ShowImageId(BaseModel):
    id: str

    class Config():
        orm_mode = True


class Image(BaseModel):
    id: str
    image: str

    class Config():
        orm_mode = True


class UserBase(BaseModel):
    email: EmailStr
    phone: constr(min_length=10, max_length=15)

    @validator("phone")
    def phone_validation(cls, v):
        regex = r"^(\+)[1-9][0-9\-\(\)\.]{9,15}$"
        if v and not re.search(regex, v, re.I):
            raise ValueError("Phone Number Invalid.")
        return v
    password: str = Field(..., example="password123")


class User(UserBase):

    class Config():
        orm_mode = True


class UserAuth(BaseModel):
    email: str
    password: str


class ShowUser(BaseModel):

    id: str
    email: str
    phone: str

    is_verified: bool

    user_details: List[ShowItem] = []

    image_user: List[Image] = []

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
    username: str


class CreateOTP(BaseModel):
    recipient_id: str


class VerifyOTP(BaseModel):
    otp_code: str


class OTPList(VerifyOTP):
    otp_failed_count: str
