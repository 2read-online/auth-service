"""Configuration"""
from pydantic import BaseSettings, Field


class Config(BaseSettings):
    """App configuration"""
    mongodb_url: str = Field(
        description='MongoDB URL with credentials e.g. mongodb:user:pwd@server:port',
        default='mongodb://root:root@mongo:27017')

    salt: str = Field(description='Salt for hashing passwords', default='salty')
    authjwt_secret_key: str = Field(description='Secret key for JWT',
                                    alias='secret_key', default='secret')


CONFIG = Config()