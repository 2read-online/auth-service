"""Module with encryption functions
"""
import hashlib
import os

SALT = os.getenv('SALT', 'e17e55ff5000cd5afe17d507c03c337cb4c')


def hash_password(password: str) -> str:
    """
    Hash password with salt
    :param password:
    :return:
    """
    return hashlib.sha256((SALT + password).encode()).hexdigest()
