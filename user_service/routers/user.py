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
from roles import *

router = APIRouter(
    prefix='/user',
    tags=['Users'],
)

get_db = database.get_db


@router.post('/', status_code=201, response_model=schemas.UserPhone)
async def register(request: schemas.UserPhone,
                   db: Session = Depends(get_db)):

    user_phone_check = db.query(models.User).filter(
        models.User.phone == request.phone).first()

    if (request.phone[0] != "+"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Please provide a valid phone number")

    elif user_phone_check is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"User with this phone no already exists!")

    elif request.password == "" or request.password is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Password can't be left blank!")

    else:
        new_user = models.User(id=str(uuid.uuid4()),
                               phone=request.phone,
                               password=Hash.bcrypt(request.password),
                               role="U",
                               liked_by=[],
                               friends=[],
                               likes=[])

    await asyncio.sleep(0.25)

    try:
        otps.send_otp(type="Phone", recipient_id=new_user.id,
                      db=db, email=new_user.email)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error occured due to {e}")

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    print(new_user.id)

    return {
        "user_id": new_user.id,
        "phone": new_user.phone,
        "password": new_user.password
    }


@router.put('/email/{id}', status_code=status.HTTP_202_ACCEPTED)
async def update_email(id,
                       request: schemas.UserEmail,
                       db: Session = Depends(get_db),
                       current_user: schemas.User = Depends(get_current_user)):

    object = db.query(models.User).filter(
        models.User.id == id)

    if not object.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Object with this {id} not found")

    user_email_check = db.query(models.User).filter(
        models.User.email == request.email).first()

    if user_email_check is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"User with this email already exists!")

    await asyncio.sleep(0.5)

    try:
        object.first().is_email_verified = False
        db.commit()
        otps.send_otp(type="Email", recipient_id=id,
                      db=db, email=request.email)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error occured due to {e}")

    object.update(dict(email=request.email))
    db.commit()
    await asyncio.sleep(0.5)

    return 'OTP Code has been sent to your email, Please proceed to verification!'


@router.get('/', response_model=List[schemas.ShowIdUser])
async def all(db: Session = Depends(database.get_db),
              dependencies=Depends(allow_create_resource),
              ):
    objects = db.query(models.User).all()
    await asyncio.sleep(0.5)
    return objects


@router.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT)
async def destroy(id,
                  db: Session = Depends(get_db),
                  current_user: schemas.User = Depends(get_current_user)):

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
async def update(id,
                 request: schemas.UserPhone,
                 db: Session = Depends(get_db),
                 current_user: schemas.User = Depends(get_current_user)):

    object = db.query(models.User).filter(
        models.User.id == id)
    if not object.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Object with this {id} not found")

    user_phone_check = db.query(models.User).filter(
        models.User.phone == request.phone).first()

    if (request.phone[0] != "+"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Please provide a valid phone number")

    elif user_phone_check is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"User with this phone no already exists!")

    elif request.password == "" or request.password is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Password can't be left blank!")

    else:

        await asyncio.sleep(0.25)

        try:
            object.first().is_phone_verified = True
            db.commit()
            otps.send_otp(type="Phone", recipient_id=id,
                          db=db)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error occured due to {e}")

        object.update(dict(phone=request.phone,
                           password=Hash.bcrypt(request.password)))
        db.commit()
        await asyncio.sleep(0.5)
        return 'Updated Successfully'


@router.get('/{id}', status_code=200, response_model=schemas.ShowUser)
async def show(id,
               response: Response,
               db: Session = Depends(get_db),
               current_user: schemas.User = Depends(get_current_user)):

    object = db.query(models.User).filter(
        models.User.id == id).first()
    if not object:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with the id {id} not found")
    await asyncio.sleep(0.5)
    return object


@router.get('/userdetails/{id}', status_code=200, response_model=schemas.ShowUserDetails)
async def show_userdetail(id,
                          db: Session = Depends(get_db),
                          current_user: schemas.User = Depends(get_current_user)):

    object = db.query(models.User).filter(
        models.User.id == id).first()
    if not object:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with the id {id} not found")
    await asyncio.sleep(0.5)
    return object


@router.get('/userimages/{id}', status_code=200, response_model=schemas.ShowImageList)
async def show_userimages(id,
                          db: Session = Depends(get_db),
                          current_user: schemas.User = Depends(get_current_user)):

    object = db.query(models.User).filter(
        models.User.id == id).first()
    if not object:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with the id {id} not found")
    await asyncio.sleep(0.5)
    return object


@router.get('/userlocation/{id}', status_code=200, response_model=schemas.ShowUserLocation)
async def show_userlocation(id,
                            db: Session = Depends(get_db),
                            current_user: schemas.User = Depends(get_current_user)):

    object = db.query(models.User).filter(
        models.User.id == id).first()
    if not object:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with the id {id} not found")
    await asyncio.sleep(0.5)
    return object


@router.get('/friendlist/{id}', status_code=200, response_model=schemas.Friends)
async def show_friendslist(id,
                           db: Session = Depends(get_db),
                           current_user: schemas.User = Depends(get_current_user)):

    object = db.query(models.User).filter(
        models.User.id == id).first()
    if not object:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with the id {id} not found")
    await asyncio.sleep(0.5)
    return object


@router.delete('delete/friend/', status_code=200)
async def delete_friend(request: schemas.DeleteFriends,
                        db: Session = Depends(get_db),
                        user: schemas.User = Depends(get_current_user)):

    object = db.query(models.User).filter(
        models.User.id == user['user_id'])
    if not object.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with the id not found")
    obj = object.first().friends
    frnlist = list(obj)

    if request.friend_id not in obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"you are not friends with this user!")

    frnlist.pop(request.friend_id)
    db.commit()

    # length = len(obj)
    # for i in range(length):
    #     if obj[i] == request.friend_id:
    #         obj[i].delete(synchronize_session=False)
    #         db.commit()

    return 'Friend Removed SuccessFully!'
