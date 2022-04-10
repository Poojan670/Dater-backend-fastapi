import asyncio
from fastapi import APIRouter, File, UploadFile, Depends, HTTPException, status
import database
import schemas
from sqlalchemy.orm import Session
import models
from .oauth2 import get_current_user
from roles import *
import shutil
import os

router = APIRouter(
    prefix='/images',
    tags=['User Images'],
)

get_db = database.get_db


def save_file(filename, data):
    with open(filename, 'wb') as f:
        f.write(data)


AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION")
S3_Bucket = os.getenv("S3_Bucket")
S3_Key = os.getenv("S3_Key")


@router.post("/")
async def upload_user_image(file: UploadFile = File(...),
                            db: Session = Depends(get_db),
                            current_user: schemas.User = Depends(get_current_user)):

    user_check = db.query(models.User).filter(
        models.User.id == current_user['user_id']).first()
    if user_check is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"User not Found!")

    file_location = f"media/{file.filename}"

    with open(file_location, "wb+") as file_object:
        shutil.copyfileobj(file.file, file_object)

    object = models.ImagesModel(
        image=file_location,
        user_image_id=current_user['user_id'])

    db.add(object)
    db.commit()
    db.refresh(object)

    return object


@router.post("/list")
async def upload_image_list(files: List[UploadFile] = File(...),
                            db: Session = Depends(get_db),
                            current_user: schemas.User = Depends(get_current_user)):

    user_check = db.query(models.User).filter(
        models.User.id == current_user['user_id']).first()
    if user_check is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"User not Found!")

    for file in files:
        file_location = f"media/{file.filename}"

        with open(file_location, "wb+") as file_object:
            shutil.copyfileobj(file.file, file_object)

        object = models.ImagesModel(image=file_location,
                                    user_image_id=current_user['user_id'])

        db.add(object)
        db.commit()
        db.refresh(object)

    return 'Uploaded Successfully!'


@router.get("/all", response_model=List[schemas.ShowImageId])
async def all_images(db: Session = Depends(get_db),
                     dependencies=Depends(allow_create_resource)):

    objects = db.query(models.ImagesModel).all()
    await asyncio.sleep(0.5)
    return objects


@router.get("/{id}", status_code=200, response_model=schemas.ImageRetrieve)
async def retrieve_image(id,
                         db: Session = Depends(get_db),
                         current_user: schemas.User = Depends(get_current_user)):

    object = db.query(models.ImagesModel).filter(
        models.ImagesModel.id == id).first()
    if not object:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Image Object with the id {id} not found")
    await asyncio.sleep(0.5)
    return object


@router.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT)
async def destroy(id,
                  db: Session = Depends(get_db),
                  current_user: schemas.User = Depends(get_current_user)):
    object = db.query(models.ImagesModel).filter(
        models.ImagesModel.id == id)

    if not object.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Image Object with this {id} not found")

    await asyncio.sleep(0.5)

    file_location = object.first().image

    os.remove(file_location)

    object.delete(synchronize_session=False)
    db.commit()
    return 'Deleted Successfully'


@router.put('/{id}', status_code=status.HTTP_202_ACCEPTED)
async def update_image(id,
                       db: Session = Depends(get_db),
                       file: UploadFile = File(...),
                       current_user: schemas.User = Depends(get_current_user)):

    object = db.query(models.ImagesModel).filter(
        models.ImagesModel.id == id)
    if not object.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Image Object with this {id} not found")

    pre_file_location = object.first().image

    try:
        os.remove(pre_file_location)
    except Exception as e:
        print(str(e))

    file_location = f"media/{file.filename}"

    with open(file_location, "wb+") as file_object:
        shutil.copyfileobj(file.file, file_object)

    await asyncio.sleep(0.5)

    object.update(dict(image=file_location))

    db.commit()

    await asyncio.sleep(0.5)

    return 'Updated Successfully'
