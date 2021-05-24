import logging
import os

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
        logger.warning('Email index alread ycreated')
    return users
