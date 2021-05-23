import logging

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel

from starlette.requests import Request
from starlette.responses import JSONResponse

from app.schemas import LoginRequest
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException

logging.basicConfig(level='DEBUG')

app = FastAPI()

origins = [
    "http://2read.online",
    "https://2read.online",
    "http://localhost",
    "http://localhost:3000",
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
    if req.email != "test" or req.password != "test":
        raise HTTPException(status_code=401, detail="Bad email or password")
    access_token = authorize.create_access_token(subject=req.email)
    return {"access_token": access_token}


@app.get('/auth/logout')
def user(authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    return {}
