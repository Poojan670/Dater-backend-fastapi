import uuid
from database import Base
from sqlalchemy import Column, Text, Integer,ForeignKey, String
from sqlalchemy.orm import relationship

class ImagesModel(Base):

    __tablename__ = 'user_images'

    id = Column('id', Text(length=36), default=lambda: str(
        uuid.uuid4()), primary_key=True)

    image = Column(String)

    user_image_id = Column(Integer)
