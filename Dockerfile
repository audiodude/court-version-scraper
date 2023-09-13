# syntax=docker/dockerfile:1.4
FROM --platform=$BUILDPLATFORM python:3.10-alpine AS builder

WORKDIR /app

RUN apk update && apk add libmemcached-dev gcc libc-dev zlib-dev

COPY requirements.txt /app
RUN --mount=type=cache,target=/root/.cache/pip \
    pip3 install --upgrade pip && pip3 install -r requirements.txt

COPY . /app

EXPOSE 8080

ENV GUNICORN_CMD_ARGS="--bind=0.0.0.0:8080 --log-file=-"
CMD ["gunicorn", "app:app"]
