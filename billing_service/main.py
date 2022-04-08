from fastapi import FastAPI, Depends, File, UploadFile, Response, HTTPException, status, Form
from sqlalchemy.orm import Session
from database import get_db, engine
import models
import shutil
from typing import List
import asyncio
import os

app = FastAPI()

models.Base.metadata.create_all(engine)


@app.post('/', status_code=200)
async def dater_plus_page(
        header: str = Form(...),
        sub_title: str = Form(...),
        sub_description: str = Form(...),
        footer: str = Form(...),
        footer_description: str = Form(...),
        file: UploadFile = File(...),
        db: Session = Depends(get_db)):

    a = file.filename
    file_location = f"media/{a}"

    try:
        with open(file_location, "wb+") as file_object:
            shutil.copyfileobj(file.file, file_object)

    except FileNotFoundError:
        os.mkdir(os.path.join("media"))

        with open(file_location, "wb+") as file_object:
            shutil.copyfileobj(file.file, file_object)

    dater = models.DaterPlusModel(
        header=header,
        sub_title=sub_title,
        sub_description=sub_description,
        footer=footer,
        footer_description=footer_description,
        img_url=file_location
    )

    await asyncio.sleep(0.5)

    db.add(dater)
    db.commit()
    db.refresh(dater)

    return dater


@app.get("/all", response_model=List[models.PremiumShowId])
async def all_images(db: Session = Depends(get_db)):
    objects = db.query(models.DaterPlusModel).all()
    await asyncio.sleep(0.5)
    return objects


@app.get("/{id}", status_code=200, response_model=models.PremiumRetrieve)
async def retrieve_image(id,
                         response: Response,
                         db: Session = Depends(get_db)):

    object = db.query(models.DaterPlusModel).filter(
        models.DaterPlusModel.id == id).first()
    if not object:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Image Object with the id {id} not found")
    await asyncio.sleep(0.5)
    return object


@app.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT)
async def destroy(id,
                  db: Session = Depends(get_db)
                  ):
    object = db.query(models.DaterPlusModel).filter(
        models.DaterPlusModel.id == id)

    if not object.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Image Object with this {id} not found")

    await asyncio.sleep(0.5)

    object.delete(synchronize_session=False)
    db.commit()
    return 'Deleted Successfully'


@app.put('/{id}', status_code=status.HTTP_202_ACCEPTED)
async def update_image(id,
                       header: str = Form(...),
                       sub_title: str = Form(...),
                       sub_description: str = Form(...),
                       footer: str = Form(...),
                       footer_description: str = Form(...),
                       db: Session = Depends(get_db),
                       file: UploadFile = File(...)
                       ):

    object = db.query(models.DaterPlusModel).filter(
        models.DaterPlusModel.id == id)
    if not object.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Image Object with this {id} not found")

    await asyncio.sleep(0.5)

    try:
        file_location = f"media/{file.filename}"
    except:
        os.mkdir(os.path.join("media"))

    with open(file_location, "wb+") as file_object:
        shutil.copyfileobj(file.file, file_object)

    object.update(header=header,
                  sub_title=sub_title,
                  sub_description=sub_description,
                  footer=footer,
                  footer_description=footer_description,
                  img_url=file_location)

    db.commit()

    await asyncio.sleep(0.5)

    return 'Updated Successfully'
