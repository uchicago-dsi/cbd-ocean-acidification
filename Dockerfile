# syntax=docker/dockerfile:1
FROM python:3.9-slim-bullseye
WORKDIR /src
RUN pip install --upgrade pip
COPY requirements.txt requirements.txt
RUN python -m pip install --no-cache-dir -r requirements.txt
COPY . .
RUN python setup.py install
ENTRYPOINT [ "python", "./main.py" ]