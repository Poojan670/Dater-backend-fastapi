from pydantic import BaseModel

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
