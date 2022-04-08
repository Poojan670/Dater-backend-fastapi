from sqlalchemy.orm import Session
from .. import models
from .. import schemas
from fastapi import HTTPException, status
import uuid


def get_all(db: Session):
    objects = db.query(models.WelcomeModel).all()
    return objects


def create(request: schemas.WelcomeBase, db: Session):
    objects = db.query(models.WelcomeModel).all()
    length = len(objects)
    if length < 4:
        obj = db.query(models.ImageWelcomeModel).filter().first()
        new_object = models.WelcomeModel(sub_title=request.sub_title,
                                         sub_description=request.sub_description, imgid=obj.id)
        db.add(new_object)
        db.commit()
        db.refresh(new_object)
        return new_object
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="You can only create four  Welcome Objects in the application")


def delete(id: uuid, db: Session):
    object = db.query(models.WelcomeModel).filter(
        models.WelcomeModel.id == id)
    if not object.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Object with this {id} not found")
    object.delete(synchronize_session=False)
    db.commit()
    return 'Deleted Successfully'


def update(id: uuid, request: schemas.Welcome, db: Session):
    object = db.query(models.WelcomeModel).filter(
        models.WelcomeModel.id == id)
    if not object.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Object with this {id} not found")
    object.update(dict(request))
    db.commit()
    return 'Updated Successfully'


def retrieve(id: uuid, db: Session):
    object = db.query(models.WelcomeModel).filter(
        models.WelcomeModel.id == id).first()
    if not object:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Object with the id {id} not found")
    return object
