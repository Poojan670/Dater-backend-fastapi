from sqlalchemy.orm import Session
import models
import schemas
from fastapi import status, HTTPException, UploadFile, File
import uuid


def get_all(db: Session):
    objects = db.query(models.ImageWelcomeModel).all()
    return objects


def create(request: schemas.ImageWelcome, db: Session, file: UploadFile):
    objects = db.query(models.ImageWelcomeModel).all()
    if objects is None:
        new_object = models.ImageWelcomeModel(
            title=request.title, description=request.description, image=file.filename)
        db.add(new_object)
        db.commit()
        db.refresh(new_object)
        return new_object
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="You can only create one Image Welcome Object in the application")


def delete(id: uuid, db: Session):
    object = db.query(models.ImageWelcomeModel).filter(
        models.ImageWelcomeModel.id == id)
    if not object.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Object with this {id} not found")
    object.delete(synchronize_session=False)
    db.commit()
    return 'Deleted Successfully'


def update(id: uuid, request: schemas.Welcome, db: Session):
    object = db.query(models.ImageWelcomeModel).filter(
        models.ImageWelcomeModel.id == id)
    if not object.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Object with this {id} not found")
    object.update(dict(request))
    db.commit()
    return 'Updated Successfully'


def retrieve(id: uuid, db: Session):
    object = db.query(models.ImageWelcomeModel).filter(
        models.ImageWelcomeModel.id == id).first()
    if not object:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Object with the id {id} not found")
    return object
