"""Configuration"""
from cryptography.fernet import Fernet
from pydantic import BaseSettings, Field, AnyUrl


class Config(BaseSettings):
    """App configuration"""
    mongodb_url: AnyUrl = Field(
        'mongodb://root:root@mongo:27017',
        description='MongoDB URL with credentials e.g. mongodb:user:pwd@server:port')
    redis_url: AnyUrl = Field(
        'redis://redis:6379/0',
        description="Redis URL")
    authjwt_secret_key: str = Field('secret', description='Secret key for JWT',
                                    env='secret_key', alias='secret_key')
    email_verification_ttl: int = Field(
        15 * 60, description='TTL for email verification (default 15 minutes)')
    fernet_key: bytes = Field(Fernet.generate_key(), description='Key for verification hash')


CONFIG = Config()
