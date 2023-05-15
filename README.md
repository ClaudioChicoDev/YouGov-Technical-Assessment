# FastAPI-Redis Dockerized Application - Star Wars API
This is an advanced FastAPI application that fetches data from the Star Wars API (https://swapi.dev/documentation).


## Features
- Containerized with Docker and Docker Compose. The application is run in a container and Redis is run in a separate container both defined in the docker-compose.yml file.
- Uses FastAPI as the web framework. An ASGI server (Uvicorn or Gunicorn) can be selected in the .env file.
- Uses Redis for cache storage (with a short, but configurable TTL in seconds).
- Health check endpoint to verify the application and Redis connection.
- CORS enabled by default and configurable in the .env file.
- API documentation with Swagger UI and ReDoc. http://localhost:8000/docs or http://localhost:8000/redoc (port may vary depending on your .env file configuration).
- Schema validation using Pydantic.
- Retrieves data from the Star Wars API concurrently.
- Uses a standard Python concurrent strategy suitable for generalization.
- Generates a CSV file from the retrieved data and saves it to disk.
- Sends the CSV file to https://httpbin.org/post using a POST request.
- Logs directly to console with the appropriate log level.
- Handles exceptions and errors raising HTTPException with appropriate status codes and messages.
- Includes comprehensive API testing of all endpoints in cache and no-cache modes.


## Endpoints
This application provides several API endpoints:

- GET /healthcheck: Provides a health check for the application and Redis connection.
- GET /: Returns basic information about the API.
- GET /characters/top_10_sorted: Returns a list of top 10 Star Wars characters (per movie appearance), sorted by their height. Caching can be enabled or disabled using the use_cache query parameter.

For more information, please refer to the API documentation.


## Requirements
This application has been dockerized and you are expected to use Docker and Docker Compose to run it. 
If you don't have Docker and/or Docker Compose, you can follow the instructions in the official documentation to install them: 

- https://docs.docker.com/get-docker/
- https://docs.docker.com/compose/install/


## Environment Variables

The .env file contains the environment variables used by Docker Compose and the application itself. The file is expected to be in the root directory of the project (at the same level as the docker-compose.yml file).

These are the minimum required parameters that you should configure:

    WEB_HOST=0.0.0.0
    WEB_PORT=8000
    WEB_SERVER=uvicorn # Valid values: uvicorn, gunicorn
    REDIS_HOST=redis
    REDIS_PORT=6379
    REDIS_PASSWORD=changeMe # Always use a strong password in production
    LOGGING_LEVEL=INFO # Valid values: DEBUG, INFO, WARNING, ERROR, CRITICAL

These are all the available parameters that can be configured. Any parameter added to the Settings class in config.py can be configured in the .env file.

    # Web server settings
    WEB_HOST=0.0.0.0
    WEB_PORT=8000
    WEB_SERVER=uvicorn # Valid values: uvicorn, gunicorn
    LOGGING_LEVEL=INFO # Valid values: DEBUG, INFO, WARNING, ERROR, CRITICAL

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

    # CORS - * is enabled by default. You can add a comma-separated list of allowed origins, methods and headers.
    ALLOWED_ORIGINS=*
    ALLOW_CREDENTIALS=True
    ALLOWED_METHODS=*
    ALLOWED_HEADERS=*


## Running the application

After setting up the .env file, you can run the application using Docker Compose. To launch the application, navigate to the project root directory and run the following command:

    docker compose up --build web

This command builds the Docker image and starts the containers defined in docker-compose.yml.

You can access the API at http://localhost:8000. 
The route for the technical assessment is http://localhost:8000/characters/top_10_sorted. 

The API documentation is available at http://localhost:8000/docs or http://localhost:8000/redoc 

*The Port may vary depending on your .env file configuration*

## Running the tests

To run the tests, navigate to the project directory and run the following command:

    
    docker compose up --build -d && docker compose run --rm web python -m pytest && docker compose down


This command builds the Docker image and runs the tests defined in the tests directory, then stops and removes the containers.


## Stopping the application

To stop the application, run the following command in the terminal:

    docker compose down

This command stops and removes the containers.