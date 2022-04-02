from fastapi import FastAPI
import uvicorn

import models
from database import engine
from routers import user, login, userdetail, otps, images

app = FastAPI()


models.Base.metadata.create_all(engine)

app.include_router(login.router)
app.include_router(user.router)
app.include_router(userdetail.router)
app.include_router(otps.router)
app.include_router(images.router)

if __name__ == '__main__':
    uvicorn.run(app, host="127.0.0.1", port=8001)
