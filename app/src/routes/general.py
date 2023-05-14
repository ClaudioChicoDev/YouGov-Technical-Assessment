from fastapi import APIRouter, Depends
from ..config import Settings
from ..schemas import AppInfo, HealthCheck
from redis import Redis
from ..utils import get_redis_client

settings = Settings()

router = APIRouter(
    tags=["General"]
)


@router.get("/healthcheck", response_model=HealthCheck)
def healthcheck(redis_client: Redis = Depends(get_redis_client)):
    """Returns the health status of the app."""
    result = {"app": "up", "redis": "disconnected"}

    if redis_client.ping():
        result["redis"] = "connected"

    return result


@router.get("/", response_model=AppInfo)
def root():
    """Returns basic information about the app."""

    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "description": settings.description,
        "author": settings.author
    }
