from dotenv import load_dotenv
from fastapi import APIRouter, Depends, status, Response, Request, HTTPException
from .. import database
from .. import schemas
from typing import List
from sqlalchemy.orm import Session
from ..repository import welcome
import jwt
import os

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

router = APIRouter(
    prefix='/welcome',
    tags=['welcome'],
)


get_db = database.get_db


@router.get('/', response_model=List[schemas.ShowWelcome])
def all(check: Request,
        db: Session = Depends(database.get_db)):

    try:
        token = check.headers.get('Authorization')
        if token is None or token == "":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=f"Not Authenticated!")

        token_data = token.split(" ")
        decode = jwt.decode(
            token_data[1], SECRET_KEY, algorithms=['HS256'])
        role = decode['role']
    except jwt.ExpiredSignatureError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"{e}")
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"{e}")

    if role == "Admin":
        return welcome.get_all(db)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Not Allowed!")


@router.post('/', status_code=status.HTTP_201_CREATED)
def create(check: Request,
           request: schemas.Welcome, db: Session = Depends(get_db)):

    try:
        token = check.headers.get('Authorization')
        if token is None or token == '':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=f"Not Authenticated!")

        token_data = token.split(" ")
        decode = jwt.decode(
            token_data[1], SECRET_KEY, algorithms=['HS256'])
        role = decode['role']
    except jwt.ExpiredSignatureError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"{e}")
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"{e}")

    if role == "Admin":
        return welcome.create(request, db)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Not Allowed!")


@router.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT)
def destroy(id,
            check: Request,
            db: Session = Depends(get_db)):

    try:
        token = check.headers.get('Authorization')
        if token is None or token == '':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=f"Not Authenticated!")

        token_data = token.split(" ")
        decode = jwt.decode(
            token_data[1], SECRET_KEY, algorithms=['HS256'])
        role = decode['role']
    except jwt.ExpiredSignatureError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"{e}")
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"{e}")

    if role == "Admin":
        return welcome.delete(id, db)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Not Allowed!")


@router.put('/{id}', status_code=status.HTTP_202_ACCEPTED)
def update(id,
           check: Request,
           request: schemas.Welcome,
           db: Session = Depends(get_db)):

    try:
        token = check.headers.get('Authorization')
        if token is None or token == '':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=f"Not Authenticated!")

        token_data = token.split(" ")
        decode = jwt.decode(
            token_data[1], SECRET_KEY, algorithms=['HS256'])
        role = decode['role']
    except jwt.ExpiredSignatureError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"{e}")
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"{e}")

    if role == "Admin":
        return welcome.update(id, request, db)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Not Allowed!")


@router.get('/{id}', status_code=200, response_model=schemas.Welcome)
def show(id, response: Response, db: Session = Depends(get_db)):
    return welcome.retrieve(id, db)
