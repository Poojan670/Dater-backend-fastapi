from fastapi import (
    APIRouter, Request,
    Depends, HTTPException,
    status, Response)
from starlette.responses import HTMLResponse, RedirectResponse
from authlib.integrations.starlette_client import OAuth, OAuthError
from starlette.config import Config
from starlette.requests import Request
import json
import database
import models
from sqlalchemy.orm import Session
import jwt

router = APIRouter(
    prefix='/google'
)

config = Config('.env')
oauth = OAuth(config)

CONF_URL = 'https://accounts.google.com/.well-known/openid-configuration'
oauth.register(
    name='google',
    server_metadata_url=CONF_URL,
    client_kwargs={
        'scope': 'openid email profile'
    }
)


@router.get('/', include_in_schema=False)
async def homepage(request: Request):
    user = request.session.get('user')
    if user:
        data = json.dumps(user)
        html = (
            f'<pre>{data}</pre>'
            '<a href="/google/logout"><button>logout</button></a>'
        )
        return HTMLResponse(html)
    # return HTMLResponse('<a href="/google/login">login</a>')

    return HTMLResponse('<div><a class="hollow button primary" href="/google/login"><img width="15px" style="margin-bottom:3px;margin-right:5px" alt="Google login" src="https://upload.wikimedia.org/wikipedia/commons/thumb/5/53/Google_%22G%22_Logo.svg/512px-Google_%22G%22_Logo.svg.png"/>Sign in with Google</a></div>')


@router.get('/login', include_in_schema=False)
async def login(request: Request):
    redirect_uri = request.url_for('auth')
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get('/auth', include_in_schema=False)
async def auth(request: Request, db: Session = Depends(database.get_db)):
    try:
        token = await oauth.google.authorize_access_token(request)
    except OAuthError as error:
        return HTMLResponse(f'<h1>{error.error}</h1>')
    user = token.get('userinfo')
    email = user['email']
    userCheck = db.query(models.User).filter(
        models.User.email == email).first()
    if userCheck is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="you are not registered!")
    elif userCheck.is_email_verified == False:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Your email isn't verified yet!")
    if user:
        request.session['user'] = dict(user)

    return RedirectResponse(url='/login/email/{}'.format(email))


@router.get('/logout', include_in_schema=False)
async def logout(request: Request,
                 response: Response):

    try:
        token = request.headers.get('Authorization')
        token_data = token.split(" ")
    except jwt.ExpiredSignatureError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"{e}")
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"{e}")

    request.session.pop('user', None)
    response.delete_cookie(key=token_data[1])
    request.session.clear()

    return RedirectResponse(url='/')
