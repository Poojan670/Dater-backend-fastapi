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
import os

router = APIRouter(
    prefix='/facebook'
)

config = Config('.env')
oauth = OAuth(config)

CONF_URL = 'https://www.facebook.com/.well-known/openid-configuration/'
oauth.register(
    name='facebook',
    server_metadata_url=CONF_URL,
    client_kwargs={
        'scope': 'openid email profile'
    }
)

CLIENT_ID = os.getenv("FACEBOOK_CLIENT_ID")


@router.get('/', include_in_schema=False)
async def fb_homepage(request: Request):
    user = request.session.get('user')
    if user:
        data = json.dumps(user)
        html = (
            f'<pre>{data}</pre>'
            '<a href="/facebook/logout"><button>logout</button></a>'
        )
        return HTMLResponse(html)

    # return HTMLResponse('<div id="fb-root"></div><script async defer crossorigin="anonymous" src="https://connect.facebook.net/en_US/sdk.js#xfbml=1&version=v13.0&appId=2543292519137671&autoLogAppEvents=1" nonce="x0DpipET"></script><div class="fb-login-button" data-width="" data-size="large" data-button-type="continue_with" data-layout="default" data-auto-logout-link="false" data-use-continue-as="false"></div>')

    return HTMLResponse('<div><a class="hollow button primary" href="/facebook/login"><img width="15px" style="margin-bottom:3px;margin-right:5px" alt="Facebook login" src="https://png.pngtree.com/element_our/png/20181117/facebook-logo-icon-png_241252.jpg"/>Sign in with Facebook</a></div>')


@router.get('/login', include_in_schema=False)
async def login(request: Request):
    # return RedirectResponse(url='https://www.facebook.com/v13.0/dialog/oauth?client_id={}&redirect_uri={"https://localhost:8000/facebook/auth"}&state={"{st=state123abc,ds=123456789}"}'.format(CLIENT_ID))
    redirect_uri = request.url_for('auth')
    return await oauth.facebook.authorize_redirect(request, redirect_uri)


@router.get('/auth', include_in_schema=False)
async def auth(request: Request, db: Session = Depends(database.get_db)):

    try:
        token = await oauth.facebook.authorize_access_token(request)
    except OAuthError as error:
        return HTMLResponse(f'<h1>{error.error}</h1>')
    user = token.get('userinfo')
    print(user)
    email = user['email']
    print(email)
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
