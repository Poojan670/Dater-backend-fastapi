import asyncio
import base64
from fastapi import APIRouter, File, UploadFile, Depends, Response, HTTPException, status
import jwt
import database
import schemas
from sqlalchemy.orm import Session
import models
from .oauth2 import get_current_user
from .producer import SendImageProducer
import json
from roles import *

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
                            db: Session = Depends(get_db),
                            current_user: schemas.User = Depends(get_current_user)):

    user_check = db.query(models.User).filter(
        models.User.id == current_user['user_id']).first()
    if user_check is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"User not Found!")

    # file_location = f"media/{file.filename}"

    # with open(file_location, "wb+") as file_object:
    #     shutil.copyfileobj(file.file, file_object)

    data = await file.read()
    encoded_image = base64.b64encode(data).decode()

    producer = SendImageProducer()

    image_obj = {"title": "Uploading User Image",
                 "id": current_user['user_id'],
                 "image": encoded_image,
                 "type": "Image"}

    producer.send_msg_async(json.dumps(
        image_obj, ensure_ascii=False, indent=4))

    object = models.ImagesModel(user_image_id=current_user['user_id'])

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
        # file_location = f"media/{file.filename}"

        # with open(file_location, "wb+") as file_object:
        #     shutil.copyfileobj(file.file, file_object)

        data = await file.read()
        encoded_image = base64.b64encode(data).decode()

        producer = SendImageProducer()

        image_obj = {"title": "Uploading User Image",
                     "id": current_user['user_id'],
                     "image": encoded_image,
                     "type": "Image"}

        producer.send_msg_async(json.dumps(
            image_obj, ensure_ascii=False, indent=4))

        object = models.ImagesModel(user_image_id=current_user['user_id'])

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
async def destroy(id,
                  db: Session = Depends(get_db),
                  current_user: schemas.User = Depends(get_current_user)):
    object = db.query(models.ImagesModel).filter(
        models.ImagesModel.id == id)

    if not object.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Image Object with this {id} not found")

    await asyncio.sleep(0.5)

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

    await asyncio.sleep(0.5)

    data = await file.read()
    encoded_image = base64.b64encode(data).decode()

    producer = SendImageProducer()

    image_obj = {"title": "Uploading User Image",
                 "id": current_user['user_id'],
                 "image": encoded_image,
                 "type": "Image"}

    producer.send_msg_async(json.dumps(
        image_obj, ensure_ascii=False, indent=4))

    object.update(dict(image=None))

    db.commit()

    await asyncio.sleep(0.5)

    return 'Updated Successfully'
