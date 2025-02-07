FROM python:3.13.1

WORKDIR /app

COPY . /app

RUN pip install -r requirements.txt