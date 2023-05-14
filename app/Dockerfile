# ./app/Dockerfile

FROM python:3.9-slim-buster

WORKDIR /app

COPY requirements.txt requirements_test.txt ./
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt -r requirements_test.txt

COPY . .

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

# Make sure the entry script is executable and run it
RUN chmod +x ./entrypoint.sh
CMD ["./entrypoint.sh"]