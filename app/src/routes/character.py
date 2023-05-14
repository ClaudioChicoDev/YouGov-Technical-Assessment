# .app/src/routes/character.py

from fastapi import APIRouter, HTTPException, status, Depends
from ..config import Settings
from ..schemas import FilmList, Character, Species, CharacterBasicInfo
from typing import List
from pydantic import ValidationError
from concurrent.futures import ThreadPoolExecutor, as_completed
from redis import Redis
from ..utils import get_redis_client
from .route_description import GET_SORTED_TOP_CHARACTERS_DESCRIPTION
import json
import requests
import pandas as pd
import os



settings = Settings()

router = APIRouter(
    prefix="/characters",
    tags=["Characters"]
)


def fetch_films_data(use_cache: bool = True):
    # Fetch films data from the API or cache if available and requested
    # The data is validated against the FilmList schema, but the validation is not strict and we use the original data
    # We'd need to validate the data thoroughly if other parts of the application depended on it, but in this case it's not necessary.
    redis_client = get_redis_client()
    cache_key = "films_data"
    cache_data = redis_client.get(cache_key)
    if bool(cache_data):
        print(f" - Cache TTL for films data: {redis_client.ttl(cache_key)} seconds")
        return json.loads(cache_data.decode("utf-8"))
    else:
        url = "https://swapi.dev/api/films"
        print(f" - Fetching films: {url}")
        response = requests.get(url)
        if response.status_code != 200:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, 
                                detail="Unable to fetch films data")
        try:
            data = response.json()
            FilmList(**data).dict()
            redis_client.setex(cache_key, settings.cache_ttl, json.dumps(data))
            return data
        except ValidationError as e:
            print(e)
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
        print(f" - Cache TTL for character data: {redis_client.ttl(cache_key)} seconds")
        return json.loads(cache_data.decode("utf-8"))
    else:
        print(f" - Fetching character: {character_url}")
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
        print(f" - Cache TTL for species data: {redis_client.ttl(cache_key)} seconds")
        return json.loads(cache_data.decode("utf-8"))
    else:
        print(f" - Fetching species: {species_url}")
        response = requests.get(species_url)
        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Unable to fetch species data")
        try:
            data = response.json()
            Species(**data).dict()
            if use_cache:
                redis_client.setex(cache_key, settings.cache_ttl, json.dumps(data))
            return data
        except ValidationError as e:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                                detail="Unable to fetch species data. API response format is invalid")


@router.get("/sorted_top_characters", response_model=List[CharacterBasicInfo], description=GET_SORTED_TOP_CHARACTERS_DESCRIPTION)
def get_sorted_top_characters(redis_client: Redis = Depends(get_redis_client), use_cache: bool = True):

    sorted_top_characters = None
    if use_cache:
        cache_data = redis_client.get("sorted_top_characters_cache")
    else:
        cache_data = None
    if bool(cache_data):
        print(
            f" - Cache TTL: {redis_client.ttl('sorted_top_characters_cache')} seconds")
        print(" - Cache found")
        sorted_top_characters = json.loads(cache_data.decode("utf-8"))
    else:
        print(" - No cache found, fetching data from API")
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
        sumarized_top_characters = {}
        for character in sorted(character_appearances.values(), key=lambda x: x["count"], reverse=True):
            sumarized_top_characters[character["url"]] = character
            if len(sumarized_top_characters) == max_characters:
                break

        # Fetch character data per character concurrently
        with ThreadPoolExecutor(max_workers=settings.max_concurrent_workers) as executor:
            future_to_url = {executor.submit(
                fetch_character_data, url): url for url in sumarized_top_characters}
            for future in as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    sumarized_top_characters[url] = future.result()
                except Exception as exc:
                    print(
                        f"Fetching character {url} raised an exception: {exc}")
                    raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                                        detail=f"Unable to fetch character data for {url}")

        # Fetch species data per character concurrently
        with ThreadPoolExecutor(max_workers=settings.max_concurrent_workers) as executor:
            future_to_url_species = {}
            for url, character in sumarized_top_characters.items():
                for species_url in character["species"]:
                    future = executor.submit(fetch_species_data, species_url)
                    future_to_url_species[(url, species_url)] = future

            for (url, species_url), future in future_to_url_species.items():
                try:
                    species_data = future.result()
                    species_index = sumarized_top_characters[url]["species"].index(species_url)
                    sumarized_top_characters[url]["species"][species_index] = species_data["name"]
                except Exception as exc:
                    print(f"Fetching species {species_url} for character {url} raised an exception: {exc}")
                    raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Unable to fetch species data for {species_url}")

        # Format species names and add the appearances count explicitly
        for url, character in sumarized_top_characters.items():
            sumarized_top_characters[url]["species"] = " & ".join(
                character["species"])
            sumarized_top_characters[url]["appearances"] = len(
                character["films"])

        # Sort characters based on height
        sorted_top_characters = sorted(sumarized_top_characters.values(
        ), key=lambda x: int(x["height"]), reverse=True)

        if use_cache:
            # Cache the result with a TTL of settings.cache_ttl
            redis_client.setex("sorted_top_characters_cache", settings.cache_ttl, json.dumps(
                sorted_top_characters))
            print(
                f" - Cache set with TTL: {settings.cache_ttl} seconds")

    # Create a CSV with the columns: name, species, height, appearances
    # It's a bit overkill to use Pandas for this simple case, but lets do it anyway.

    # Create a dataframe with the data
    df = pd.DataFrame(sorted_top_characters)

    # Select the columns we want
    df = df[["name", "species", "height", "appearances"]]

    # There's no need to rename the columns in this case, but we could do it like this:
    # df = df.rename(columns={"name": "Name", "species": "Species", "height": "Height", "appearances": "Appearances"})

    # Save the dataframe as a CSV file in the ./csv folder. Create the folder if it doesn't exist
    os.makedirs("csv", exist_ok=True)
    df.to_csv("csv/sorted_top_characters.csv", index=False)

    # Print the csv file content
    print("\n - CSV file content:")
    print(df.to_csv(index=False))

    # Send the CSV to httpbin.org
    files = {'file': open('csv/sorted_top_characters.csv', 'rb')}
    response = requests.post('https://httpbin.org/post', files=files)
    if response.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Unable to send CSV file to httpbin.org")
    else:
        print(" - CSV file sent to httpbin.org successfully")

    return sorted_top_characters