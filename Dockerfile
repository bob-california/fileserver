
FROM python:3.7-alpine

RUN apk update && apk add build-base libffi-dev libressl-dev musl-dev openssl-dev cargo

RUN pip install --upgrade pip poetry

WORKDIR /fileserver

COPY poetry.lock pyproject.toml /fileserver/

RUN poetry config virtualenvs.create false \
    && poetry install --no-dev

