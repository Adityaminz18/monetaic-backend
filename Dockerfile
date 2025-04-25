FROM python:3.14-rc-slim-bookworm

WORKDIR /app

COPY . /app

RUN pip install -r requirements.txt