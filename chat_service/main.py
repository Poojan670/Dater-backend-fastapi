from fastapi import Depends, FastAPI, status, Request, HTTPException
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel
from typing import List
import uuid
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import Session, relationship
import jwt
import json
import os
from .producer import ChatProducer

SECRET_KEY = os.getenv("SECRET_KEY")

SQLALCHEMY_DATABASE_URL = 'sqlite:///chat.db'

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={
    "check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


app = FastAPI()


class ChatBase(BaseModel):
    message: str


class Chat(ChatBase):

    class Config():
        orm_mode = True


class UserBase(BaseModel):

    id: str

    msg = List[Chat] = []

    class Config():
        orm_mode = True


class UserModel(Base):

    __tablename__ = 'user'

    id = Column(String(100), primary_key=True)

    msg = relationship("MessageModel", back_populates="user_msg")


class MessageModel(Base):

    __tablename__ = 'chat'

    id = Column(String(100), primary_key=True)

    message = Column(String(500))

    user_id = Column(Integer, ForeignKey("user.id"))

    msg_to = Column(Integer, ForeignKey("user.id"))

    user_msg = relationship("UserModel", back_populates="msg")


Base.metadata.create_all(engine)


@app.get('/user/{id}', status_code=200, response_model=UserBase)
async def get_user(id,
                   db: Session = Depends(get_db)):

    user = db.query(UserModel).filter(UserModel.id == id)
    if not object.first():
        raise HTTPException(status_code=404)
    return user


@app.post('/message', status_code=200)
async def send_message(check: Request, request: Chat,
                       db: Session = Depends(get_db)):

    try:
        token = check.headers.get('Authorization')
        token_data = token.split(" ")
        decode = jwt.decode(
            token_data[1], SECRET_KEY, algorithms=['HS256'])
        user_id = decode['user_id']
    except jwt.ExpiredSignatureError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"{e}")
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"{e}")

    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if user is None:
        user = UserModel(id=user_id)

    msg = MessageModel(id=str(uuid.uuid4()),
                       message=request.message,
                       user_id=user.id,
                       )

    try:
        producer = ChatProducer()
        chat_msg = msg
        producer.send_msg_async(json.dumps(chat_msg))
    except Exception as e:
        print("Error occured due to {}".format(str(e)))


@app.get('/message/{id}', status_code=200, response_model=Chat)
def get_message(id,
                db: Session = Depends(get_db)):

    msg = db.query(MessageModel).filter(MessageModel.id == id)
    if not object.first():
        raise HTTPException(status_code=404)
    return msg


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='127.0.0.1', port=8003, log_level='debug')
