import logging

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
from pydantic import BaseModel
from pymongo.collection import Collection
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.db import get_user_collection, User
from app.encrypt import hash_password
from app.schemas import LoginRequest, RegisterRequest

logging.basicConfig(level='DEBUG')

users: Collection = get_user_collection()

app = FastAPI()

origins = [
    "http://2read.online",
    "https://2read.online",
    "http://localhost",
    "http://localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Settings(BaseModel):
    authjwt_secret_key: str = "secret"


@AuthJWT.load_config
def get_config():
    return Settings()


@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(request: Request, exc: AuthJWTException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message}
    )


@app.put("/auth/login")
def login(req: LoginRequest, authorize: AuthJWT = Depends()):
    user_db = User.from_db(users.find_one({'email': req.email}))
    if user_db is None or user_db.hashed_password != hash_password(req.password):
        raise HTTPException(status_code=401, detail="Bad email or password")

    access_token = authorize.create_access_token(subject=req.email)
    return {"access_token": access_token}


@app.put("/auth/register")
def register(req: RegisterRequest):
    user_db = users.find_one({'email': req.email})
    if user_db is not None:
        raise HTTPException(status_code=409, detail="User already exists")

    user_db = User(email=req.email, hashed_password=hash_password(req.password))
    users.insert_one(user_db.dict(exclude_none=True))
    return {}


@app.get('/auth/logout')
def user(authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    return {}
