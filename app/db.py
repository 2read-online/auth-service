import logging
import os
from datetime import datetime
from typing import Any, Optional

from bson import ObjectId
from bson.errors import InvalidId
from pydantic import BaseModel, EmailStr, BaseConfig, Field
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.errors import OperationFailure

logger = logging.getLogger('db')


def get_user_collection():
    mongo_db_server = os.getenv('MONGO_DB_SERVER', 'mongo')
    client = MongoClient(f'mongodb://%s:%s@{mongo_db_server}:27017/' % ('root', 'e8520c749249e517e'))
    db: Database = client.prod
    users: Collection = db.users

    try:
        users.create_index('email', unique=True)
    except OperationFailure as err:
        logger.warning('Email index already created')
    return users


class OID(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        try:
            return ObjectId(str(v))
        except InvalidId:
            raise ValueError("Not a valid ObjectId")


class User(BaseModel):
    id: Optional[OID] = Field(alias='_id')
    email: EmailStr
    hashed_password: str

    class Config(BaseConfig):
        allow_population_by_field_name = True  # << Added
        json_encoders = {
            datetime: lambda dt: dt.isoformat(),
            ObjectId: lambda oid: str(oid),
        }

    @classmethod
    def from_db(cls, obj: dict):
        if obj is None:
            return None

        return User(**obj)
