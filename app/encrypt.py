import hashlib
import os

SALT = os.getenv('SALT', 'e17e55ff5000cd5afe17d507c03c337cb4c')


def hash_password(password: str) -> str:
    return hashlib.sha256((SALT + password).encode()).hexdigest()
