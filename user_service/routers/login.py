from posixpath import split
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
from .oauth2 import get_current_user

router = APIRouter(
    prefix='/user',
    tags=['authentication'],
)


@router.post('/login')
def login(request: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
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
    access_token = token.create_access_token(data={"sub": user.phone})
    refresh_token = token.create_refresh_token(data={"subs": user.phone})
    return {"access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"}


class TokenSchema(BaseModel):
    refresh_token: str


@router.post('/refresh')
def refresh_token(request: TokenSchema = Depends()):
    refresh_token = request.refresh_token
    decode = token.decode_token(refresh_token)
    new_access_token = token.create_access_token(data={"sub": decode})
    return {
        "access_token": new_access_token
    }


# @router.get("/logout")
# def logout(response: Response, request: Request):
#     user = request.headers.get('Authorization')
#     access_token = "user.split("Bearer")"
#     print(access_token)
#     # response = RedirectResponse('/login', status_code=302)
#     # response.delete_cookie(key=user)
    # return response
