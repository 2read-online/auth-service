"""Redis Module (needed for mocking)"""
from redis import Redis


def make_redis(url: str) -> Redis:
    """Make a Redis client"""
    return Redis.from_url(url)
