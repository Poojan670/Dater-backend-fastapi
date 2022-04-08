from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from pydantic import BaseModel
import uvicorn
import models
from database import engine, SessionLocal
from routers import (
    user, login,
    userdetail, otps,
    images, google,
    password, location,
    friendrequest, report,
    like
)
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from typing import Optional
from hashing import Hash
import os


# Initialize FastAPI
app = FastAPI()

origins = [
    "http://localhost:3000",
]

app.add_middleware(SessionMiddleware,
                   secret_key=os.getenv('SECRET_KEY'))

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


models.Base.metadata.create_all(engine)


class AdminBase(BaseModel):
    phone: str
    password: str
    is_phone_verified: bool


@app.on_event("startup")
async def startup_event():
    with SessionLocal() as db:
        try:
            admin_check = db.query(models.User).filter(
                models.User.phone == 'admin').first()
            if admin_check is None:
                admin = models.User(id='10712b93-470d-43ca-8fef-3ffb3598b9e3',
                                    phone='admin',
                                    email='emocrest@gmail.com',
                                    password=Hash.bcrypt("poojan12"),
                                    is_phone_verified=True,
                                    is_email_verified=True,
                                    role="A",
                                    friends=[])
                db.add(admin)
                db.commit()
                db.refresh(admin)
                print("Superuser created Successfully!")
            else:
                print("Okay!")
        except Exception as e:
            print(str(e))

app.include_router(login.router)
app.include_router(google.router)
app.include_router(user.router)
app.include_router(password.router)
app.include_router(userdetail.router)
app.include_router(otps.router)
app.include_router(images.router)
app.include_router(location.router)
app.include_router(friendrequest.router)
app.include_router(report.router)
app.include_router(like.router)


async def get_user(request: Request) -> Optional[dict]:
    user = request.session.get('user')
    if user is not None:
        return user
    else:
        raise HTTPException(
            status_code=403, detail='Could not validate credentials.')


@app.route('/openapi.json')
async def get_open_api_endpoint(request: Request, user: Optional[dict] = Depends(get_user)):
    response = JSONResponse(get_openapi(
        title='FastAPI', version=1, routes=app.routes))
    return response


@app.get('/docs', tags=['documentation'])
async def get_documentation(request: Request, user: Optional[dict] = Depends(get_user)):
    response = get_swagger_ui_html(
        openapi_url='/openapi.json', title='Documentation')
    return response


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='127.0.0.1', port=8000, log_level='debug')
