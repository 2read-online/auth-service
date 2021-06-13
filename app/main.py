"""Web application"""
import logging

from fastapi import FastAPI, HTTPException, Depends
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
from pymongo.collection import Collection
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.config import CONFIG
from app.db import get_user_collection, User
from app.encrypt import hash_password
from app.schemas import LoginRequest, RegisterRequest

logging.basicConfig(level='DEBUG')

users: Collection = get_user_collection()

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
def login(req: LoginRequest, authorize: AuthJWT = Depends()):
    """Process login request
    """
    user_db = User.from_db(users.find_one({'email': req.email}))
    if user_db is None or user_db.hashed_password != hash_password(req.password):
        raise HTTPException(status_code=401, detail="Bad email or password")

    access_token = authorize.create_access_token(subject=str(user_db.id))
    return {"access_token": access_token}


@app.post("/auth/register")
def register(req: RegisterRequest):
    """Process user registration request
    """
    user_db = users.find_one({'email': req.email})
    if user_db is not None:
        raise HTTPException(status_code=409, detail="User already exists")

    user_db = User(email=req.email, hashed_password=hash_password(req.password))
    users.insert_one(user_db.dict(exclude_none=True))
    return {}


@app.get('/auth/logout')
def user(authorize: AuthJWT = Depends()):
    """Process logout request
    """
    authorize.jwt_required()
    return {}
