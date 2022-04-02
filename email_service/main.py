from fastapi import FastAPI
import uvicorn

import models
from database import engine

app = FastAPI()


models.Base.metadata.create_all(engine)


if __name__ == '__main__':
    uvicorn.run(app, host="127.0.0.1", port=8001)
