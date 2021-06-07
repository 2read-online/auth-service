"""Module with encryption functions
"""
import hashlib

from app.config import CONFIG


def hash_password(password: str) -> str:
    """
    Hash password with salt
    :param password:
    :return:
    """
    return hashlib.sha256((CONFIG.salt + password).encode()).hexdigest()
