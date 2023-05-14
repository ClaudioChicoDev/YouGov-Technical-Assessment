from pydantic import BaseSettings, validator
from typing import List, Optional


class Settings(BaseSettings):

    # General settings
    app_name: str = "Fancy Star Wars API Service"
    app_version: str = "0.0.1"
    description: Optional[str] = "This fancy API service provides information about Star Wars characters. It's been put together as a technical assestment for a job application. It's not very useful, but it's fancy."
    author: Optional[str] = "Claudio Chico"

    # Redis settings
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: Optional[str] = None

    # Concurrency settings (for internal concurrent functions)
    max_concurrent_workers: int = 5

    # Cache settings
    cache_ttl: int = 10  # in seconds

    # CORS
    allowed_origins: List[str] = []
    allow_credentials: bool = True
    allowed_methods: List[str] = []
    allowed_headers: List[str] = []

    @validator("allowed_origins", "allowed_methods", "allowed_headers", pre=True)
    def parse_lists(cls, v):
        """Parse comma-separated lists"""
        return [s.strip() for s in v.split(',')] if isinstance(v, str) else v

    class Config:
        env_file = ".env"
