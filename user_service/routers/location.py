from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session
import database
import schemas
import models
import roles
from .oauth2 import get_current_user
import uuid
import asyncio
from typing import Optional

router = APIRouter(
    prefix='/user/location',
    tags=['User Location']
)

get_db = database.get_db


@router.post('/', status_code=200)
async def current_location(request: schemas.LocationBase,
                           db: Session = Depends(get_db),
                           user: schemas.User = Depends(get_current_user)):

    object = db.query(models.UserLocation).filter(
        models.UserLocation.user_id == user['user_id']).first()
    if object:
        db.delete(object)
        db.commit()

    await asyncio.sleep(0.25)

    location = models.UserLocation(
        id=str(uuid.uuid4()),
        longitude=request.longitude,
        latitude=request.latitude,
        location_name=request.location_name,
        user_id=user['user_id']
    )
    db.add(location)
    db.commit()
    db.refresh(location)

    return location


@router.get('/', status_code=200, response_model=List[schemas.AllLocation])
async def get_all_user_location(db: Session = Depends(database.get_db),
                                dependencies=Depends(roles.allow_create_resource)):

    objects = db.query(models.UserLocation).all()
    await asyncio.sleep(0.25)
    return objects


@router.delete('/{id}', status_code=204)
async def destroy(id,
                  db: Session = Depends(get_db),
                  current_user: schemas.User = Depends(get_current_user)):

    object = db.query(models.UserLocation).filter(
        models.UserLocation.id == id)
    if not object.first():
        raise HTTPException(
            status_code=404, detail=f"UserLocation with this {id} not found")

    await asyncio.sleep(0.5)
    object.delete(synchronize_session=False)
    db.commit()
    return 'Deleted Successfully'


@router.get('/{id}', status_code=200, response_model=schemas.LocationBase)
async def show(id,
               db: Session = Depends(get_db),
               current_user: schemas.User = Depends(get_current_user)):

    object = db.query(models.UserLocation).filter(
        models.UserLocation.id == id).first()
    if not object:
        raise HTTPException(status_code=404,
                            detail=f"User with the id {id} not found")
    await asyncio.sleep(0.5)
    return object


@router.get('/search', status_code=200, response_model=List[schemas.LocationFilter])
async def get_all_user_location(location: Optional[str] = None,
                                db: Session = Depends(database.get_db),
                                user: schemas.User = Depends(get_current_user)):

    objects = db.query(models.UserLocation)

    if location:
        objects = objects.filter(models.UserLocation.location_name == location)

    return objects.all()
