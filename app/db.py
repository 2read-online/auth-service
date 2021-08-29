"""Module for working with MongoDB"""
import logging
from pydantic import BaseModel, EmailStr
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.errors import OperationFailure

from pydantic_mongo import MongoModel

from app.config import CONFIG

logger = logging.getLogger('db')


def get_user_collection():
    """Get or setup user collection from MongoDB"""
    client = MongoClient(CONFIG.mongodb_url)
    db: Database = client.prod
    users: Collection = db.users

    try:
        users.create_index('email', unique=True)
    except OperationFailure:
        logger.warning('Email index already created')
    return users


class User(MongoModel):
    """User model
    """
    email: EmailStr
