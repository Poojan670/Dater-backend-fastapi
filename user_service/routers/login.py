from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import Response, RedirectResponse
from pydantic import BaseModel
import models
import database
from sqlalchemy.orm import Session
from hashing import Hash
from routers import token
from fastapi.security import OAuth2PasswordRequestForm
from schemas import BaseModel

router = APIRouter(
    prefix='/user',
    tags=['authentication'],
)


@router.post('/login')
def login(request: OAuth2PasswordRequestForm = Depends(),
          db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(
        models.User.phone == request.username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Invalid Credentials")
    if not Hash.verify(request.password, user.password):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Incorrect Password")
    if user.is_phone_verified == False:
        raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
                            detail="You are not a verified user!")
    access_token = token.create_access_token(data={"sub": user.phone,
                                                   "user_id": user.id,
                                                   "role": user.role})
    refresh_token = token.create_refresh_token(data={"sub": user.phone,
                                                     "user_id": user.id,
                                                     "role": user.role})
    return {"access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"}


class TokenSchema(BaseModel):
    refresh_token: str


@router.post('/refresh')
def refresh_token(request: TokenSchema = Depends()):
    refresh_token = request.refresh_token
    decode = token.decode_token(refresh_token)
    new_access_token = token.create_access_token(data={"sub": decode['sub'],
                                                       "user_id": decode['user_id'],
                                                       "role": decode['role']})
    return {
        "access_token": new_access_token
    }


import jwt


@router.get("/logout")
def logout(request: Request):
    try:
        token = request.headers.get('Authorization')
        token_data = token.split(" ")
    except jwt.ExpiredSignatureError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"{e}")
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"{e}")

    response = RedirectResponse('/login', status_code=302)
    response.delete_cookie(key=token_data[1])
    return "Successfully Logged Out!"
