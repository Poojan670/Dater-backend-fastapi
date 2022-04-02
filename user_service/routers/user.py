from hashlib import new
from fastapi import APIRouter, Depends, HTTPException, status, Response
import database
import schemas
from sqlalchemy.orm import Session
import models
from hashing import Hash
from .oauth2 import get_current_user
from typing import List
from . import otps
import uuid
import asyncio


router = APIRouter(
    prefix='/user',
    tags=['Users'],
)

get_db = database.get_db


@router.post('/', status_code=201, response_model=schemas.User)
async def register(request: schemas.User, db: Session = Depends(get_db)):

    user_email_check = db.query(models.User).filter(
        models.User.email == request.email).first()

    user_phone_check = db.query(models.User).filter(
        models.User.phone == request.phone).first()

    if (request.phone[0] != "+"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Please provide a valid phone number")

    elif user_email_check is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"User with this email already exists!")

    elif user_phone_check is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"User with this phone no already exists!")

    elif request.password == "" or request.password is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Password can't be left blank!")
    else:
        new_user = models.User(id=str(uuid.uuid4()),
                               phone=request.phone,
                               email=request.email,
                               password=Hash.bcrypt(request.password))

        await asyncio.sleep(1)

        try:
            otps.send_otp(type="Email", recipient_id=new_user.id,
                          db=db, email=new_user.email)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error occured due to {e}")

        await asyncio.sleep(1)

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        print(new_user.id)

        return {
            "id": new_user.id,
            "email": new_user.email,
            "phone": new_user.phone,
            "password": new_user.password
        }


@router.get('/', response_model=List[schemas.ShowIdUser])
async def all(db: Session = Depends(database.get_db), current_user: schemas.User = Depends(get_current_user)):
    objects = db.query(models.User).all()
    await asyncio.sleep(0.5)
    return objects


@router.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT)
async def destroy(id, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_user)):
    object = db.query(models.User).filter(
        models.User.id == id)
    if not object.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"User with this {id} not found")

    await asyncio.sleep(0.5)
    object.delete(synchronize_session=False)
    db.commit()
    return 'Deleted Successfully'


@router.put('/{id}', status_code=status.HTTP_202_ACCEPTED)
async def update(id, request: schemas.User, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_user)):
    object = db.query(models.User).filter(
        models.User.id == id)
    if not object.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Object with this {id} not found")
    object.update(dict(phone=request.phone, email=request.email,
                  password=Hash.bcrypt(request.password)))
    db.commit()
    await asyncio.sleep(0.5)
    return 'Updated Successfully'


@router.get('/{id}', status_code=200, response_model=schemas.ShowUser)
async def show(id, response: Response, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_user)):
    object = db.query(models.User).filter(
        models.User.id == id).first()
    if not object:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with the id {id} not found")
    await asyncio.sleep(0.5)
    return object
