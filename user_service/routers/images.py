import asyncio
import os
from fastapi import APIRouter, File, UploadFile, Depends, Response, HTTPException, status
from typing import List
import database
import schemas
from sqlalchemy.orm import Session
import models
import shutil
from .oauth2 import get_current_user

router = APIRouter(
    prefix='/images',
    tags=['User Images'],
)

get_db = database.get_db


def save_file(filename, data):
    with open(filename, 'wb') as f:
        f.write(data)


@router.post("/")
async def upload_user_image(file: UploadFile = File(...),
                            db: Session = Depends(get_db)):

    file_location = f"media/{file.filename}"

    with open(file_location, "wb+") as file_object:
        shutil.copyfileobj(file.file, file_object)

    object = models.ImagesModel(image=file_location,
                                user_image_id="ea0bc52f-ae56-49f6-8451-c32a53d33857")

    db.add(object)
    db.commit()
    db.refresh(object)

    return object


@router.post("/list")
async def upload_image_list(files: List[UploadFile] = File(...), db: Session = Depends(get_db)):

    for file in files:
        file_location = f"media/{file.filename}"

        with open(file_location, "wb+") as file_object:
            shutil.copyfileobj(file.file, file_object)

        object = models.ImagesModel(image=file_location,
                                    user_image_id="fa269bb7-9751-4151-b8ef-f0b6f448103b")

        db.add(object)
        db.commit()
        db.refresh(object)

    return {"Uploaded Filenames": [file.filename for file in files]}


@router.get("/all", response_model=List[schemas.ShowImageId])
async def all_images(db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_user)):
    objects = db.query(models.ImagesModel).all()
    await asyncio.sleep(0.5)
    return objects


@router.get("/{id}", status_code=200, response_model=schemas.ImageRetrieve)
async def retrieve_image(id,
                         response: Response,
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
async def destroy(id, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_user)):
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
                       response: Response,
                       db: Session = Depends(get_db),
                       file: UploadFile = File(...),
                       current_user: schemas.User = Depends(get_current_user)):

    object = db.query(models.ImagesModel).filter(
        models.ImagesModel.id == id)
    if not object.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Image Object with this {id} not found")

    await asyncio.sleep(0.5)

    pre_file_location = object.first().image

    try:
        os.remove(pre_file_location)
    except Exception as e:
        print(str(e))

    file_location = f"media/{file.filename}"

    with open(file_location, "wb+") as file_object:
        shutil.copyfileobj(file.file, file_object)

    object.update(dict(image=file_location))

    db.commit()

    await asyncio.sleep(0.5)
    return 'Updated Successfully'
