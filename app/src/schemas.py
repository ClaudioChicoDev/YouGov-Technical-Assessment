from pydantic import BaseModel, HttpUrl
from typing import List, Optional


class HealthCheck(BaseModel):
    app: str
    redis: str


class AppInfo(BaseModel):
    name: str
    version: Optional[str] = None
    description: Optional[str] = None
    author: Optional[str] = None


class Film(BaseModel):
    characters: List[HttpUrl]


class FilmList(BaseModel):
    results: List[Film]


class Character(BaseModel):
    height: int
    films: List[HttpUrl]
    species: List[HttpUrl]


class Species(BaseModel):
    name: str


class CharacterBasicInfo(BaseModel):
    name: str
    height: int
    appearances: int
    species: str
