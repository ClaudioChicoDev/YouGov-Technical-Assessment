# ./src/utils.py

from fastapi import HTTPException, status
from redis import Redis
from .config import Settings

settings = Settings()

redis_client = None  # Global variable to store the Redis client instance


def get_redis_client():
    global redis_client

    if redis_client is None:
        # Create Redis client instance if it doesn't exist yet. If this fails we'll get a 500 error, which is fine.
        print("Initializing the redis client")
        redis_client = Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            db=settings.redis_db,
            password=settings.redis_password
        )

    return redis_client
