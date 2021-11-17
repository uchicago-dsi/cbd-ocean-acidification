# syntax=docker/dockerfile:1

FROM python:3.8.12-slim-buster
WORKDIR /src
RUN pip install --upgrade pip
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY . .