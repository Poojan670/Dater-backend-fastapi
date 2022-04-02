from fastapi import APIRouter, Depends, FastAPI, HTTPException, status, Request
import models
import database
import schemas
from sqlalchemy.orm import Session
from hashing import Hash
from routers import token
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException

router = APIRouter(
    tags=['authentication'],
)


@router.post('/login')
def login(request: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(
        models.User.email == request.username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Invalid Credentials")
    if not Hash.verify(request.password, user.password):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Incorrect Password")
    if user.is_verified == False:
        raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
                            detail="You are not a verified user!")
    access_token = token.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

# @AuthJWT.load_config
# def get_config():
#     return schemas.Settings()


# @FastAPI().exception_handler(AuthJWTException)
# def authjwt_exception_handler(request: Request, exc: AuthJWTException):
#     return JSONResponse(
#         status_code=exc.status_code,
#         content={"detail": exc.message}
#     )


# @router.post('/login')
# def login(user: schemas.User, Authorize: AuthJWT = Depends(), db: Session = Depends(database.get_db)):
#     if user.email != "test" or user.password != "test":
#         raise HTTPException(status_code=401, detail="Bad username or password")

#     users = db.query(models.User).filter(
#         models.User.email == user.username).first()
#     if not users:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
#                             detail=f"Invalid Credentials")
#     if not Hash.verify(users.password, user.password):
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
#                             detail=f"Incorrect Password")
#     if users.is_verified == False:
#         raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
#                             detail="You are not a verified user!")

#     # Use create_access_token() and create_refresh_token() to create our
#     # access and refresh tokens
#     access_token = Authorize.create_access_token(subject=user.email)
#     refresh_token = Authorize.create_refresh_token(subject=user.email)
#     return {"access_token": access_token,
#             "refresh_token": refresh_token,
#             "token_type": "bearer"}


# @router.post('/refresh')
# def refresh(Authorize: AuthJWT = Depends()):
#     """
#     The jwt_refresh_token_required() function insures a valid refresh
#     token is present in the request before running any code below that function.
#     we can use the get_jwt_subject() function to get the subject of the refresh
#     token, and use the create_access_token() function again to make a new access token
#     """
#     Authorize.jwt_refresh_token_required()

#     current_user = Authorize.get_jwt_subject()
#     new_access_token = Authorize.create_access_token(subject=current_user)
#     return {"access_token": new_access_token}


# @router.get('/protected')
# def protected(Authorize: AuthJWT = Depends()):
#     Authorize.jwt_required()

#     current_user = Authorize.get_jwt_subject()
#     return {"user": current_user}
