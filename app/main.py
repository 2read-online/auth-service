"""Web application"""
import logging

from fastapi import FastAPI, HTTPException, Depends
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
from pymongo.collection import Collection
from starlette.requests import Request
from starlette.responses import JSONResponse
from cryptography.fernet import Fernet, InvalidToken

from app.config import CONFIG
from app.db import get_user_collection, User
from app.make_redis import make_redis
from app.schemas import LoginRequest, VerifyRequest

logging.basicConfig(level='DEBUG')
logger = logging.getLogger(__name__)

users: Collection = get_user_collection()
redis = make_redis(CONFIG.redis_url)

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
    fernet = Fernet(CONFIG.fernet_key)
    redis.xadd('/auth/login',
               dict(email=req.email, verification_hash=fernet.encrypt(bytes(req.email, 'utf-8'))),
               maxlen=100)
    return {}


@app.post("/auth/verify")
def verify(req: VerifyRequest, authorize: AuthJWT = Depends()):
    """Verify email
    """
    fernet = Fernet(CONFIG.fernet_key)
    try:
        email = fernet.decrypt(bytes(req.verification_hash, 'ascii'),
                               ttl=CONFIG.email_verification_ttl)
        email = str(email, 'utf-8')
    except InvalidToken as err:
        logger.error('Failed to decrypt verification hash: %s', err)
        raise HTTPException(status_code=400, detail="Bad or expired verification link") from err

    user_db = User.from_db(users.find_one({'email': email}))
    if user_db is None:
        logger.info('Record a new user with email=%s', email)
        user_db = User(email=email)
        user_id = str(users.insert_one(user_db.db()))
    else:
        user_id = str(user_db.id)

    logger.info('Generate token for ID %s', user_id)
    access_token = authorize.create_access_token(subject=user_id)
    refresh_token = authorize.create_refresh_token(subject=user_id)
    return {'email': email, 'access_token': access_token, 'refresh_token': refresh_token}


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
