import asyncio
import os
from fastapi import FastAPI, File, UploadFile, Depends, Response, HTTPException, status, Request
import jwt
from typing import List
import database
import schemas
from sqlalchemy.orm import Session
import models
import shutil
import os
from dotenv import load_dotenv

load_dotenv()


SECRET_KEY = os.getenv('SECRET_KEY')

app = FastAPI(prefix='/images',
              tags=['User Images'],)


get_db = database.get_db


def save_file(filename, data):
    with open(filename, 'wb') as f:
        f.write(data)


async def get_user_id(check: Request):
    token = check.headers.get('Authorization')
    token_data = token.split(" ")
    decode = jwt.decode(
        token_data[1], SECRET_KEY, algorithms=['HS256'])
    user_id = decode['user_id']
    await asyncio.sleep(0.5)
    return user_id


@app.post("/")
async def upload_user_image(file: UploadFile = File(...),
                            db: Session = Depends(get_db)):

    file_location = f"media/{file.filename}"

    with open(file_location, "wb+") as file_object:
        shutil.copyfileobj(file.file, file_object)

    object = models.ImagesModel(image=file_location,
                                user_image_id=get_user_id)

    db.add(object)
    db.commit()
    db.refresh(object)

    return object


@app.post("/list")
async def upload_image_list(files: List[UploadFile] = File(...),
                            db: Session = Depends(get_db)):

    for file in files:
        file_location = f"media/{file.filename}"

        with open(file_location, "wb+") as file_object:
            shutil.copyfileobj(file.file, file_object)

        object = models.ImagesModel(image=file_location,
                                    user_image_id=get_user_id)

        db.add(object)
        db.commit()
        db.refresh(object)

    return {"Uploaded Filenames": [file.filename for file in files]}


@app.get("/all", response_model=List[schemas.ShowImageId])
async def all_images(db: Session = Depends(get_db)):
    objects = db.query(models.ImagesModel).all()
    await asyncio.sleep(0.5)
    return objects


@app.get("/{id}", status_code=200, response_model=schemas.ImageRetrieve)
async def retrieve_image(id,
                         response: Response,
                         db: Session = Depends(get_db),
                        ):
    object = db.query(models.ImagesModel).filter(
        models.ImagesModel.id == id).first()
    if not object:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Image Object with the id {id} not found")
    await asyncio.sleep(0.5)
    return object


@app.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT)
async def destroy(id,
                  db: Session = Depends(get_db)
                  ):
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


@app.put('/{id}', status_code=status.HTTP_202_ACCEPTED)
async def update_image(id,
                       response: Response,
                       db: Session = Depends(get_db),
                       file: UploadFile = File(...),
                       ):

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


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='127.0.0.1', port=8002)
