# ./app/src/app.py

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from .config import Settings
from .routes import general, character
from .utils import get_redis_client
import logging

settings = Settings()

logging.basicConfig(level=logging.getLevelName(settings.logging_level))
logger = logging.getLogger(__name__)
logger.info("Logging level set to %s (%s)" % (settings.logging_level, logging.getLevelName(settings.logging_level)))
app = FastAPI()

# Middlewares
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=settings.allow_credentials,
    allow_methods=settings.allowed_methods,
    allow_headers=settings.allowed_headers
)


# Routes
app.include_router(general.router, dependencies=[Depends(get_redis_client)])
app.include_router(character.router, dependencies=[Depends(get_redis_client)])