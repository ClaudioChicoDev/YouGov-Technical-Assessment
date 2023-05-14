from fastapi.testclient import TestClient
from src.app import app
from src.config import Settings
from src import schemas
from src.routes.character import fetch_films_data, fetch_character_data, fetch_species_data
import requests
import time
import os
import pandas as pd


settings = Settings()

client = TestClient(app)


def test_healthcheck():
    response = client.get("/healthcheck")
    assert response.status_code == 200
    assert response.json().get("app") == "up"
    assert response.json().get("redis") == "connected"
    assert schemas.HealthCheck(**response.json())


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json().get("name") == "Fancy Star Wars API Service"
    assert schemas.AppInfo(**response.json())


def test_404_route():
    response = client.get("/this_doesnt_exist")
    assert response.status_code == 404
    assert response.json() == {"detail": "Not Found"}


def test_fetch_films_data_without_cache():
    # Call the fetch_films_data function
    films_data = fetch_films_data(use_cache=False)

    # Assert the expected results
    assert films_data is not None
    assert isinstance(films_data["results"], list)
    assert schemas.FilmList(**films_data)
    assert "results" in films_data
    assert len(films_data["results"]) >= 6
    assert films_data["results"][0]["title"] == "A New Hope"

    # Test the api endpoint directly
    response = requests.get("https://swapi.dev/api/films")
    assert response.status_code == 200


def test_fetch_films_data_with_cache():
    start_time = time.time()
    films_data = fetch_films_data(use_cache=False)
    first_fetch_time = time.time() - start_time

    # Assert the expected results
    assert films_data is not None
    assert isinstance(films_data["results"], list)
    assert schemas.FilmList(**films_data)
    assert "results" in films_data
    assert len(films_data["results"]) >= 6
    assert films_data["results"][0]["title"] == "A New Hope"

    # Call the function twice to test the cache
    films_data = fetch_films_data(use_cache=True)
    start_time = time.time()
    films_data = fetch_films_data(use_cache=True)
    second_fetch_time = time.time() - start_time

    # Assert the expected results
    assert films_data is not None
    assert isinstance(films_data["results"], list)
    assert schemas.FilmList(**films_data)
    assert "results" in films_data
    assert len(films_data["results"]) >= 6
    assert films_data["results"][0]["title"] == "A New Hope"


def test_fetch_character_data_without_cache():
    # Call the fetch_character_data function
    character_data = fetch_character_data(
        "https://swapi.dev/api/people/1/", use_cache=False)

    # Assert the expected results
    assert character_data is not None
    assert isinstance(character_data, dict)
    assert schemas.Character(**character_data)
    assert character_data["name"] == "Luke Skywalker"

    # Test the api endpoint directly
    response = requests.get("https://swapi.dev/api/people/1/")
    assert response.status_code == 200


def test_fetch_character_data_with_cache():
    start_time = time.time()
    character_data = fetch_character_data(
        "https://swapi.dev/api/people/1/", use_cache=False)
    first_run_time = time.time() - start_time

    # Assert the expected results
    assert character_data is not None
    assert isinstance(character_data, dict)
    assert schemas.Character(**character_data)
    assert character_data["name"] == "Luke Skywalker"

    # Call the function twice to test the cache
    character_data = fetch_character_data("https://swapi.dev/api/people/1/", use_cache=True)
    start_time = time.time()
    character_data = fetch_character_data("https://swapi.dev/api/people/1/", use_cache=True)
    second_run_time = time.time() - start_time

    # Assert the expected results
    assert character_data is not None
    assert isinstance(character_data, dict)
    assert schemas.Character(**character_data)
    assert character_data["name"] == "Luke Skywalker"


def test_fetch_species_data_without_cache():
    # Call the fetch_species_data function
    species_data = fetch_species_data(
        "https://swapi.dev/api/species/2/", use_cache=False)

    # Assert the expected results
    assert species_data is not None
    assert isinstance(species_data, dict)
    assert schemas.Species(**species_data)
    assert species_data["name"] == "Droid"

    # Test the api endpoint directly
    response = requests.get("https://swapi.dev/api/species/2/")
    assert response.status_code == 200


def test_fetch_species_data_with_cache():
    # Call the fetch_species_data function (once to populate the cache)
    start_time = time.time()
    species_data = fetch_species_data(
        "https://swapi.dev/api/species/2/", use_cache=False)
    first_run_time = time.time() - start_time

    # Assert the expected results
    assert species_data is not None
    assert isinstance(species_data, dict)
    assert schemas.Species(**species_data)
    assert species_data["name"] == "Droid"

    # Call the function twice to test the cache
    species_data = fetch_species_data("https://swapi.dev/api/species/2/", use_cache=True)
    start_time = time.time()
    species_data = fetch_species_data("https://swapi.dev/api/species/2/", use_cache=True)
    second_run_time = time.time() - start_time

    # Assert the expected results
    assert species_data is not None
    assert isinstance(species_data, dict)
    assert schemas.Species(**species_data)
    assert species_data["name"] == "Droid"


def test_top_10_sorted_without_cache():
    response = client.get("/characters/top_10_sorted?use_cache=False")
    assert response.status_code == 200
    top_10_sorted = response.json()
    assert isinstance(top_10_sorted, list)
    assert len(top_10_sorted) == 10
    for character in top_10_sorted:
        assert schemas.CharacterBasicInfo(**character)

    # Confirm that the first character is Chewbacca
    assert top_10_sorted[0]["name"] == "Chewbacca"
    assert top_10_sorted[0]["height"] == 228
    assert top_10_sorted[0]["appearances"] == 4
    assert top_10_sorted[0]["species"] == "Wookie"

    # Confirm that the last character is Yoda
    assert top_10_sorted[-1]["name"] == "Yoda"
    assert top_10_sorted[-1]["height"] == 66
    assert top_10_sorted[-1]["appearances"] == 5
    assert top_10_sorted[-1]["species"] == "Yoda's species"


def test_top_10_sorted_with_cache():
    # Make the first request without using the cache
    response = client.get("/characters/top_10_sorted?use_cache=False")

    assert response.status_code == 200
    top_10_sorted = response.json()
    assert isinstance(top_10_sorted, list)
    assert len(top_10_sorted) == 10
    for character in top_10_sorted:
        assert schemas.CharacterBasicInfo(**character)

    # Confirm that the first character is Chewbacca
    assert top_10_sorted[0]["name"] == "Chewbacca"
    assert top_10_sorted[0]["height"] == 228
    assert top_10_sorted[0]["appearances"] == 4
    assert top_10_sorted[0]["species"] == "Wookie"

    # Make new requests using the cache
    response = client.get("/characters/top_10_sorted?use_cache=True")
    response = client.get("/characters/top_10_sorted?use_cache=True")

    assert response.status_code == 200
    top_10_sorted = response.json()
    assert isinstance(top_10_sorted, list)
    assert len(top_10_sorted) == 10
    for character in top_10_sorted:
        assert schemas.CharacterBasicInfo(**character)

    # Confirm that the first character is Chewbacca
    assert top_10_sorted[0]["name"] == "Chewbacca"
    assert top_10_sorted[0]["height"] == 228
    assert top_10_sorted[0]["appearances"] == 4
    assert top_10_sorted[0]["species"] == "Wookie"


def test_csv_generation():
    # Generate the CSV by calling the API endpoint
    response = client.get("/characters/top_10_sorted", params={"use_cache": False})
    assert response.status_code == 200

    # Make sure the CSV file exists
    assert os.path.isfile('csv/top_10_sorted.csv')

    # Load the CSV into a DataFrame
    df = pd.read_csv('csv/top_10_sorted.csv')

    # Check the shape of the DataFrame
    assert df.shape[0] == 10  # Exactly ten rows
    assert df.shape[1] == 4  # Exactly four columns

    # Check the columns are as expected
    assert list(df.columns) == ["name", "species", "height", "appearances"]

    # Check the data types of the columns
    assert df['name'].dtype == object # pandas dtype for strings is object
    assert df['species'].dtype == object # pandas dtype for strings is object
    assert df['height'].dtype == int
    assert df['appearances'].dtype == int

    # Make sure the characters are sorted by height in descending order
    assert all(df['height'][i] >= df['height'][i+1] for i in range(len(df['height'])-1))
