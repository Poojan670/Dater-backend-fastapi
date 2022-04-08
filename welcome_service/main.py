from fastapi import FastAPI, File

from . import models
from .database import engine
# from database import engine
# from .database import engine
from .routers import welcome, image_welcome

app = FastAPI()


models.Base.metadata.create_all(engine)

app.include_router(welcome.router)
app.include_router(image_welcome.router)
