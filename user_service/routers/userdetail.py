from datetime import date
from fastapi import APIRouter, Depends, status, HTTPException, Response, Request
import database
import schemas
from sqlalchemy.orm import Session
import models
from .oauth2 import get_current_user
from typing import List
import asyncio
from roles import *

router = APIRouter(
    prefix='/detail',
    tags=['User Details'],
)

get_db = database.get_db


@router.post('/', status_code=201, response_model=schemas.UserDetails)
def create_userdetail(request: schemas.UserDetails,
                      db: Session = Depends(get_db),
                      current_user: schemas.User = Depends(get_current_user)):

    user_check = db.query(models.User).filter(
        models.User.id == current_user['user_id']).first()
    if user_check is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"User not Found!")

    user_check = db.query(models.UserDetails).filter(
        models.UserDetails.user_id == current_user['user_id']).first()
    if user_check is not None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"You already have created your user details, Please update it!")

    user_detail = models.UserDetails(

        first_name=request.first_name,

        middle_name=request.middle_name,

        last_name=request.last_name,

        age=request.age,

        birthday=request.birthday,

        gender=request.gender,

        sexuality=request.sexuality,

        social_media=request.social_media,

        passions=request.passions,

        profession=request.profession,

        hobbies=request.hobbies,

        user_id=current_user['user_id'],
    )
    if user_detail.age == 0 or user_detail.age >= 100:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User cant have {user_detail.age} as age")

    elif user_detail.birthday == date.today():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"You can't have today's date as your birthday!")

    db.add(user_detail)
    db.commit()
    db.refresh(user_detail)
    return user_detail


@router.get('/', status_code=status.HTTP_200_OK, response_model=List[schemas.ShowIdUserDetails])
def get_userdetail(db: Session = Depends(get_db),
                   dependencies=Depends(allow_create_resource),):

    user_details = db.query(models.UserDetails).all()
    return user_details


@router.get('/{id}', status_code=200, response_model=schemas.UserDetails)
async def show_userdetail(id,
                          response: Response,
                          db: Session = Depends(get_db),
                          current_user: schemas.User = Depends(get_current_user)):

    object = db.query(models.UserDetails).filter(
        models.UserDetails.id == id).first()
    if not object:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with the id {id} not found")
    await asyncio.sleep(0.5)
    return object


@router.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT)
async def destroy(id, db: Session = Depends(get_db),
                  current_user: schemas.User = Depends(get_current_user)):

    object = db.query(models.UserDetails).filter(
        models.UserDetails.id == id)
    if not object.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"User with this {id} not found")

    await asyncio.sleep(0.5)

    object.delete(synchronize_session=False)
    db.commit()
    return 'Deleted Successfully'


@router.put('/{id}', status_code=status.HTTP_202_ACCEPTED)
async def update(id,
                 request: schemas.UserDetails,
                 db: Session = Depends(get_db),
                 current_user: schemas.User = Depends(get_current_user)):

    object = db.query(models.UserDetails).filter(
        models.UserDetails.id == id)
    if not object.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Object with this {id} not found")
    object.update(dict(first_name=request.first_name,

                       middle_name=request.middle_name,

                       last_name=request.last_name,

                       age=request.age,

                       birthday=request.birthday,

                       gender=request.gender,

                       sexuality=request.sexuality,

                       social_media=request.social_media,

                       passions=request.passions,

                       profession=request.profession,

                       living_in=request.living_in))

    db.commit()
    await asyncio.sleep(0.5)
    return 'Updated Successfully'
