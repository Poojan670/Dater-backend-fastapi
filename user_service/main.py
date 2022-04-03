from fastapi import FastAPI, Request, HTTPException, Depends
import uvicorn
import models
from database import engine
from routers import user, login, userdetail, otps, images, google
from starlette.middleware.sessions import SessionMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from typing import Optional

# Initialize FastAPI
app = FastAPI()
app.add_middleware(SessionMiddleware,
                   secret_key='09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7')


models.Base.metadata.create_all(engine)

app.include_router(login.router)
app.include_router(google.router)
app.include_router(user.router)
app.include_router(userdetail.router)
app.include_router(otps.router)
app.include_router(images.router)


# Try to get the logged in user
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
