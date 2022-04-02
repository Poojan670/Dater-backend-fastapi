from pydantic import BaseModel, constr
from typing import List, Optional


class WelcomeBase(BaseModel):
    sub_title: constr(max_length=20)
    sub_description: constr(max_length=60)


class Welcome(WelcomeBase):

    class Config():
        orm_mode = True


class ShowWelcome(BaseModel):
    id: str

    class Config():
        orm_mode = True


class ImageWelcome(BaseModel):

    title: constr(max_length=20)

    description: constr(max_length=60)

    image_url: Optional[str] = None


class ShowImageWelcome(BaseModel):

    title: str

    description: str

    image: Optional[str]

    welcome: List[ShowWelcome]

    class Config():
        orm_mode = True


class ShowIDImageWelcome(BaseModel):
    id: str

    class Config():
        orm_mode = True
