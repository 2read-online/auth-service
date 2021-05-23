import os

from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

from app.encrypt import hash_password


def get_user_collection():
    mongo_db_server = os.getenv('MONGO_DB_SERVER', 'mongo')
    client = MongoClient(f'mongodb://%s:%s@{mongo_db_server}:27017/' % ('root', 'e8520c749249e517e'))
    db: Database = client.prod
    users: Collection = db.users

    if users.count_documents({'email': 'atimin@gmail.com'}) == 0:
        users.insert_one({
            'email': "atimin@gmail.com",
            'hashed_password': hash_password('pwd')
        })

        users.create_index('email', unique=True)
    return users
