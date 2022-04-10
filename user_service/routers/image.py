import os
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from fastapi.datastructures import UploadFile
from fastapi.exceptions import HTTPException
from fastapi.param_functions import File, Body
from images.s3_utils import S3_SERVICE
from images.utils import *
from dotenv import load_dotenv
import datetime
import database
import schemas
import models
from .oauth2 import get_current_user
from roles import *
import asyncio
import boto
from boto.s3.key import Key
import nest_asyncio
nest_asyncio.apply()

load_dotenv()
project_name = "FastAPI"


AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.environ.get("AWS_REGION")
S3_Bucket = os.environ.get("S3_Bucket")
S3_Key = os.environ.get("S3_Key")
AWS_DEFAULT_ACL = None


router = APIRouter(prefix='/user/image',
                   tags=['User Image!'])

# Object of S3_SERVICE Class
s3_client = S3_SERVICE(
    AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION, AWS_DEFAULT_ACL)


@router.get("/ping", status_code=200, description="***** Liveliness Check *****")
async def ping():
    return {"ping": "pong"}


async def delete_image_s3(id):
    s3conn = boto.connect_s3(AWS_ACCESS_KEY_ID,
                             AWS_SECRET_ACCESS_KEY)
    bucket = s3conn.get_bucket(S3_Bucket)

    k = Key(bucket)
    k.key = str(id)
    k.delete()


@router.post("/upload", status_code=200, description="***** Upload png asset to S3 *****")
async def upload(fileobject: UploadFile = File(...),
                 db: Session = Depends(database.get_db),
                 user: schemas.User = Depends(get_current_user),
                 ):

    userCheck = db.query(models.User).filter(
        models.User.id == user['user_id']).first()
    if userCheck is None:
        raise HTTPException(status_code=400, detail="User Not Found!")

    filename = fileobject.filename
    current_time = datetime.datetime.now()
    # split the file name into two different path (string + extention)
    split_file_name = os.path.splitext(filename)
    # for realtime application you must have genertae unique name for the file
    file_name_unique = str(current_time.timestamp()).replace('.', '')
    file_extension = split_file_name[1]  # file extention
    data = fileobject.file._file  # Converting tempfile.SpooledTemporaryFile to io.BytesIO
    uploads3 = await s3_client.upload_fileobj(bucket=S3_Bucket, key=S3_Key + file_name_unique + file_extension, fileobject=data)

    if uploads3:
        s3_url = f"https://{S3_Bucket}.s3.{AWS_REGION}.amazonaws.com/{S3_Key}/{file_name_unique +  file_extension}"

        try:
            user_image = models.ImagesModel(user_id=user["user_id"],
                                            image_url=s3_url)

            db.add(user_image)
            db.commit()
            db.refresh(user_image)

        except Exception as e:
            return "Error Occured due to {} ".format(str(e))

        # response added
        return {"status": "success", "image_url": s3_url, "detail": "Image Uploaded Successfully!"}

    else:
        raise HTTPException(status_code=400, detail="Failed to upload in S3")


@router.get("/all", response_model=List[schemas.ShowImageId])
async def all_images(db: Session = Depends(database.get_db),
                     dependencies=Depends(allow_create_resource)):

    objects = db.query(models.ImagesModel).all()
    return objects


@router.get("/{id}", status_code=200, response_model=schemas.ImageRetrieve)
async def retrieve_image(id,
                         db: Session = Depends(database.get_db),
                         user: schemas.User = Depends(get_current_user)):

    object = db.query(models.ImagesModel).filter(
        models.ImagesModel.id == id).first()
    if not object:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Image Object with the id {id} not found")
    await asyncio.sleep(0.5)
    return object


@router.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT)
async def destroy(id,
                  db: Session = Depends(database.get_db),
                  user: schemas.User = Depends(get_current_user)):
    object = db.query(models.ImagesModel).filter(
        models.ImagesModel.id == id)

    if not object.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Image Object with this {id} not found")

    await asyncio.sleep(0.5)

    img = object.first().image_url

    try:
        asyncio.run(delete_image_s3(img))
    except Exception as e:
        return "Error occured due to {}".format(str(e))

    object.delete(synchronize_session=False)
    db.commit()

    return 'Deleted Successfully'


@router.put('/{id}', status_code=status.HTTP_202_ACCEPTED)
async def update_image(id,
                       db: Session = Depends(database.get_db),
                       fileobject: UploadFile = File(...),
                       user: schemas.User = Depends(get_current_user)):

    object = db.query(models.ImagesModel).filter(
        models.ImagesModel.id == id)
    if not object.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Image Object with this {id} not found")

    filename = fileobject.filename
    current_time = datetime.datetime.now()
    # split the file name into two different path (string + extention)
    split_file_name = os.path.splitext(filename)
    # for realtime application you must have genertae unique name for the file
    file_name_unique = str(current_time.timestamp()).replace('.', '')
    file_extension = split_file_name[1]  # file extention
    data = fileobject.file._file  # Converting tempfile.SpooledTemporaryFile to io.BytesIO
    uploads3 = await s3_client.upload_fileobj(bucket=S3_Bucket, key=S3_Key + file_name_unique + file_extension, fileobject=data)

    if uploads3:
        s3_url = f"https://{S3_Bucket}.s3.{AWS_REGION}.amazonaws.com/{S3_Key}{file_name_unique +  file_extension}"

        try:
            object.update(dict(image_url=s3_url))

            db.commit()

        except Exception as e:
            return "Error Occured due to {} ".format(str(e))

        return {"status": "success", "image_url": s3_url, "detail": "Updated Successfuly"}

    else:
        raise HTTPException(status_code=400, detail="Failed to upload in S3")
