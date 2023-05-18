# ./app/src/routes/character.py

from fastapi import APIRouter, HTTPException, status, Depends
from ..config import Settings
from ..schemas import FilmList, Character, Species, CharacterBasicInfo
from typing import List
from pydantic import ValidationError
from concurrent.futures import ThreadPoolExecutor, as_completed
from redis import Redis
from ..utils import get_redis_client
from .route_description import GET_TOP_10_SORTED_DESCRIPTION
import json
import requests
import pandas as pd
import os
import logging


logger = logging.getLogger(__name__)

settings = Settings()

router = APIRouter(
    prefix="/characters",
    tags=["Characters"]
)


def fetch_films_data(use_cache: bool = True):
    # Fetch films data from the API or cache if available and requested
    # The data is validated against the FilmList schema, but the validation is not strict and we use the original data
    # We'd need to validate the data thoroughly if other parts of the application depended on it, but in this case it's not necessary.
    cache_data = None
    if use_cache:
        redis_client = get_redis_client()
        cache_key = "films_data"
        cache_data = redis_client.get(cache_key)
    if bool(cache_data):
        logger.info(f" - Cache TTL for films data: {redis_client.ttl(cache_key)} seconds")
        return json.loads(cache_data.decode("utf-8"))
    else:
        url = "https://swapi.dev/api/films"
        logger.info(f" - Fetching films: {url}")
        response = requests.get(url)
        if response.status_code != 200:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, 
                                detail="Unable to fetch films data")
        try:
            data = response.json()
            FilmList(**data).dict()
            if use_cache:
                redis_client.setex(cache_key, settings.cache_ttl, json.dumps(data))
            return data
        except ValidationError as e:
            logger.error(e)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                                detail="Unable to fetch films data. API response format is invalid")


def fetch_character_data(character_url: str, use_cache: bool = True):
    # Fetch character data from the API or cache if available and requested
    # The data is validated against the Character schema, but the validation is not strict and we use the original data
    # We'd need to validate the data thoroughly if other parts of the application depended on it, but in this case it's not necessary.
    cache_data = None
    if use_cache:
        redis_client = get_redis_client()
        cache_key = f"character_data:{character_url}"
        cache_data = redis_client.get(cache_key)
    if bool(cache_data):
        logger.info(f" - Cache TTL for character data: {redis_client.ttl(cache_key)} seconds")
        return json.loads(cache_data.decode("utf-8"))
    else:
        logger.info(f" - Fetching character: {character_url}")
        response = requests.get(character_url)
        if response.status_code != 200:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                                detail="Unable to fetch character data")
        try:
            data = response.json()
            Character(**data).dict()
            if use_cache:
                redis_client.setex(cache_key, settings.cache_ttl, json.dumps(data))
            return data
        except ValidationError as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                                detail="Unable to fetch character data. API response format is invalid")


def fetch_species_data(species_url: str, use_cache: bool = True):
    # Fetch species data from the API or cache if available and requested
    # The data is validated against the Species schema, but the validation is not strict and we use the original data
    # We'd need to validate the data thoroughly if other parts of the application depended on it, but in this case it's not necessary.
    cache_data = None
    if use_cache:
        redis_client = get_redis_client()
        cache_key = f"species_data:{species_url}"
        cache_data = redis_client.get(cache_key)
    if bool(cache_data):
        logger.info(f" - Cache TTL for species data: {redis_client.ttl(cache_key)} seconds")
        return json.loads(cache_data.decode("utf-8"))
    else:
        logger.info(f" - Fetching species: {species_url}")
        response = requests.get(species_url)
        if response.status_code != 200:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, 
                                detail="Unable to fetch species data")
        try:
            data = response.json()
            Species(**data).dict()
            if use_cache:
                redis_client.setex(cache_key, settings.cache_ttl, json.dumps(data))
            return data
        except ValidationError as e:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                                detail="Unable to fetch species data. API response format is invalid")


@router.get("/top_10_sorted", response_model=List[CharacterBasicInfo], description=GET_TOP_10_SORTED_DESCRIPTION)
def get_top_10_sorted(redis_client: Redis = Depends(get_redis_client), use_cache: bool = True):

    top_10_sorted = None
    if use_cache:
        cache_data = redis_client.get("top_10_sorted_cache")
    else:
        cache_data = None
    if bool(cache_data):
        logger.info(f" - Cache TTL: {redis_client.ttl('top_10_sorted_cache')} seconds")
        top_10_sorted = json.loads(cache_data.decode("utf-8"))
    else:
        logger.info(" - No cache found, fetching data from API")
        #this could be dynamic but the request was to use 10 characters only
        max_characters = 10

        # Fetch films data
        films_data = fetch_films_data()

        # Count character appearances in all movies
        character_appearances = {}
        for film in films_data["results"]:
            for character_url in film["characters"]:
                if character_url not in character_appearances:
                    character_appearances[character_url] = {
                        "url": character_url,
                        "count": 0
                    }
                character_appearances[character_url]["count"] += 1

        # Sort characters based on appearance count and get top nth characters
        top_characters_data = {}
        for character in sorted(character_appearances.values(), key=lambda x: x["count"], reverse=True):
            top_characters_data[character["url"]] = character
            if len(top_characters_data) == max_characters:
                break

        # Fetch character data per character concurrently
        with ThreadPoolExecutor(max_workers=settings.max_concurrent_workers) as executor:
            futures_to_character_urls = {executor.submit(
                fetch_character_data, url): url for url in top_characters_data}
            for future in as_completed(futures_to_character_urls):
                url = futures_to_character_urls[future]
                try:
                    top_characters_data[url] = future.result()
                except Exception as exc:
                    logger.error(f"Fetching character {url} raised an exception: {exc}")
                    raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                                        detail=f"Unable to fetch character data for {url}")

        # Fetch species data per character concurrently
        with ThreadPoolExecutor(max_workers=settings.max_concurrent_workers) as executor:
            futures_to_character_urls_species = {}
            for url, character in top_characters_data.items():
                for species_url in character["species"]:
                    future = executor.submit(fetch_species_data, species_url)
                    futures_to_character_urls_species[(url, species_url)] = future

            for (url, species_url), future in futures_to_character_urls_species.items():
                try:
                    species_data = future.result()
                    species_index = top_characters_data[url]["species"].index(species_url)
                    top_characters_data[url]["species"][species_index] = species_data["name"]
                except Exception as exc:
                    logger.error(f"Fetching species {species_url} for character {url} raised an exception: {exc}")
                    raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, 
                                        detail=f"Unable to fetch species data for {species_url}")

        # Format species names and add the appearances count explicitly
        for url, character in top_characters_data.items():
            top_characters_data[url]["species"] = " & ".join(character["species"])
            top_characters_data[url]["appearances"] = len(character["films"])

        # Sort characters based on height
        top_10_sorted = sorted(top_characters_data.values(), key=lambda x: int(x["height"]), reverse=True)

        if use_cache:
            # Cache the result with a TTL of settings.cache_ttl
            redis_client.setex("top_10_sorted_cache", settings.cache_ttl, json.dumps(top_10_sorted))
            logger.info(f" - Cache set with TTL: {settings.cache_ttl} seconds")

    # Create a CSV with the columns: name, species, height, appearances
    # It's a bit overkill to use Pandas for this simple case, but lets do it anyway.

    # Create a dataframe with the data
    df = pd.DataFrame(top_10_sorted)

    # Select the columns we want
    df = df[["name", "species", "height", "appearances"]]

    # There's no need to rename the columns in this case, but we could do it like this:
    # df = df.rename(columns={"name": "Name", "species": "Species", "height": "Height", "appearances": "Appearances"})

    # Save the dataframe as a CSV file in the ./csv folder. Create the folder if it doesn't exist
    os.makedirs("csv", exist_ok=True)
    df.to_csv("csv/top_10_sorted.csv", index=False)

    # Print the csv file content
    logger.info("\n\n\nCSV file content:\n\n%s" % df.to_csv(index=False))

    # Send the CSV to httpbin.org
    with open('csv/top_10_sorted.csv', 'rb') as f:
        files = {'file': f}
        response = requests.post('https://httpbin.org/post', files=files)
        if response.status_code != 200:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, 
                                detail="Unable to send CSV file to httpbin.org")
        else:
            logger.info(" - CSV file sent to httpbin.org successfully")

    return top_10_sorted