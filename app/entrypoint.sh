#!/bin/sh
set -e

echo "Waiting 2 seconds so the database has time to start..."
sleep 2
echo "Selected server: $WEB_SERVER"
echo "Starting server..."
if [ "$WEB_SERVER" = "gunicorn" ]; then
    exec gunicorn -k uvicorn.workers.UvicornWorker -w 4 src.app:app --bind ${WEB_HOST}:${WEB_PORT}
elif [ "$WEB_SERVER" = "uvicorn" ]; then
    exec uvicorn src.app:app --host ${WEB_HOST} --port ${WEB_PORT}
else
    echo "Error: No valid server specified. Please set WEB_SERVER to either 'gunicorn' or 'uvicorn'."
    exit 1
fi