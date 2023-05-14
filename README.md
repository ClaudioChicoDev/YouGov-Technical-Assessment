# FastAPI-Redis Dockerized Application - Star Wars API
This is an advanced FastAPI application that fetches data from the Star Wars API and uses Redis for caching. The application is containerized using Docker and orchestrated using Docker Compose. It also includes detailed API testing.

For the Technical Assessment I've create the /characters/top_10_sorted endpoint.
Here is the link to the swapi API documentation that this service uses: https://swapi.dev/documentation

You can check the documentation of this service at http://localhost:8000/docs or http://localhost:8000/redoc (ports may vary depending on your .env file configuration).


## Features
- Retrieves data from the Star Wars API.
- Caches data using Redis to improve performance.
- Includes comprehensive API testing.
- Generates a CSV file from the retrieved data.
- Dockerized for easy setup and deployment.


## Endpoints
This application provides several API endpoints:

- GET /healthcheck: Provides a health check for the application and Redis connection.
- GET /: Returns basic information about the API.
- GET /characters/top_10_sorted: Returns a list of top 10 Star Wars characters (per movie appearance), sorted by their height. Caching can be enabled or disabled using the use_cache query parameter.


## Requirements
This application has been dockerized and you are expected to use Docker and Docker Compose to run it. 
If you don't have Docker and/or Docker Compose, you can follow the instructions in the official documentation to install them: 

- https://docs.docker.com/get-docker/
- https://docs.docker.com/compose/install/


## Environment Variables

The .env file contains the environment variables used by Docker Compose and the application itself:

These are the minimum required parameters that you should configure in the .env file:

    WEB_HOST=0.0.0.0
    WEB_PORT=8000
    WEB_SERVER=uvicorn # Valid values: uvicorn, gunicorn
    REDIS_HOST=redis
    REDIS_PORT=6379
    REDIS_PASSWORD=changeMe # Always use a strong password in production

These are all the available parameters that can be configured in the .env file:

    # General settings
    APP_NAME=Fancy Star Wars API Service
    APP_VERSION=0.0.1
    DESCRIPTION=This fancy API service provides information about Star Wars characters. It's been put together as a technical assestment for a job application. It's not very useful, but it's fancy.
    AUTHOR=Claudio Chico

    # Redis settings
    REDIS_HOST=localhost
    REDIS_PORT=6379
    REDIS_DB=0
    REDIS_PASSWORD= changeMe # Always use a strong password in production

    # Concurrency settings
    MAX_CONCURRENT_WORKERS=5 # This is the maximum number of workers that will be used for concurrent tasks by a single initiator

    # Cache settings
    CACHE_TTL=10  # This is the default TTL for the Redis cached data (in seconds)

    # CORS (* is enabled by default)
    ALLOWED_ORIGINS=  # Add comma-separated list of allowed origins here
    ALLOW_CREDENTIALS=True
    ALLOWED_METHODS=  # Add comma-separated list of allowed methods here
    ALLOWED_HEADERS=  # Add comma-separated list of allowed headers here


## Running the application

To run the application, navigate to the project directory and run the following command:

    docker-compose up --build web

This command builds the Docker image and starts the container for the web service defined in docker-compose.yml.

You can access the FastAPI application at http://localhost:8000 (or any other port you have defined in the .env file).

## Running the tests

To run the tests, navigate to the project directory and run the following command:

    
    docker compose run --rm --build web python -m pytest


This command builds the Docker image and runs the tests defined in the tests directory. The --rm flag removes the container after the tests have finished running. The --build flag is optional but advised, it forces the image to be rebuilt before running the tests.


## Stopping the application

To stop the application, run the following command in the terminal:

    docker-compose down

This command stops and removes the containers.