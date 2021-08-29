"""Module with encryption functions
"""
import hashlib

from app.config import CONFIG


def hash_with_salt(string: str) -> str:
    """
    Hash password with salt
    :param string:
    :return:
    """
    return hashlib.sha256((CONFIG.salt + string).encode()).hexdigest()
