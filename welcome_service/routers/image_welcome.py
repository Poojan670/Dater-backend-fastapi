from fastapi import APIRouter, Depends, status, Response
import database
import schemas
from typing import List
from sqlalchemy.orm import Session
from repository import image

router = APIRouter(
    prefix='/image',
    tags=['image_welcome'],
)


get_db = database.get_db


@router.get('/', response_model=List[schemas.ShowIDImageWelcome])
def all(db: Session = Depends(database.get_db)):
    return image.get_all(db)


@router.post('/', status_code=status.HTTP_201_CREATED)
def create(request: schemas.ImageWelcome, db: Session = Depends(get_db)):
    return image.create(request, db)


@router.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT)
def destroy(id, db: Session = Depends(get_db)):
    return image.delete(id, db)


@router.put('/{id}', status_code=status.HTTP_202_ACCEPTED)
def update(id, request: schemas.ImageWelcome, db: Session = Depends(get_db)):
    return image.update(id, request, db)


@router.get('/{id}', status_code=200, response_model=schemas.ShowImageWelcome)
def show(id, response: Response, db: Session = Depends(get_db)):
    return image.retrieve(id, db)
