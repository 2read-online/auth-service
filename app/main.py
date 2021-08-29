"""Web application"""
import logging

from fastapi import FastAPI, HTTPException, Depends
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
from pymongo.collection import Collection
from starlette.requests import Request
from starlette.responses import JSONResponse
from redis import Redis
from cryptography.fernet import Fernet, InvalidToken

from app.config import CONFIG
from app.db import get_user_collection, User
from app.encrypt import hash_with_salt
from app.schemas import LoginRequest

logging.basicConfig(level='DEBUG')
logger = logging.getLogger(__name__)
fernet_key = Fernet.generate_key()

users: Collection = get_user_collection()
redis: Redis = Redis.from_url(CONFIG.redis_url)

app = FastAPI()


@AuthJWT.load_config
def get_config():
    """Load settings
    """
    return CONFIG


@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(_request: Request, exc: AuthJWTException):
    """
    JWT exception
    :param _request:
    :param exc:
    :return:
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message}
    )


@app.put("/auth/login")
def login(req: LoginRequest):
    """Process login request
    """
    f = Fernet(fernet_key)
    redis.xadd('/auth/login',
               dict(email=req.email, verification_hash=f.encrypt(bytes(req.email, 'utf-8'))),
               maxlen=100)


@app.get("/auth/verify/{verification_hash}")
def verify(verification_hash: str, authorize: AuthJWT = Depends()):
    """Verify email
    """
    f = Fernet(fernet_key)
    try:
        email = f.decrypt(bytes(verification_hash, 'ascii'), ttl=CONFIG.email_verification_ttl)
        email = str(email, 'utf-8')
    except InvalidToken as err:
        logger.error('Failed to decrypt verification hash: %s', err)
        raise HTTPException(status_code=400, detail="Bad or expired verification link")

    user_db = User.from_db(users.find_one({'email': email}))
    if user_db is None:
        logger.info('Record a new user with email=%s', email)
        user_db = User(email=email)
        users.insert_one(user_db.db())

    user_id = str(user_db.id)
    access_token = authorize.create_access_token(subject=user_id)
    refresh_token = authorize.create_refresh_token(subject=user_id)
    return {'access_token': access_token, 'refresh_token': refresh_token}


@app.get('/auth/refresh')
def refresh(authorize: AuthJWT = Depends()):
    """Refresh access token
    """
    authorize.jwt_refresh_token_required()

    user_id = authorize.get_jwt_subject()
    new_access_token = authorize.create_access_token(subject=user_id)
    return {'access_token': new_access_token}


@app.get('/auth/logout')
def user(authorize: AuthJWT = Depends()):
    """Process logout request
    """
    authorize.jwt_required()
    return {}
