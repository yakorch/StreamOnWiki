FROM python:3.9-slim

LABEL authors="mrkorch"

RUN apt-get update
RUN pip install --upgrade pip

WORKDIR /code/services

COPY cassandra_communication/requirements.txt cassandra_communication/
RUN pip install -r cassandra_communication/requirements.txt

COPY rest_api/requirements.txt rest_api/
RUN pip install -r rest_api/requirements.txt

WORKDIR /code

ENTRYPOINT uvicorn services.rest_api.gateaway:app --host 0.0.0.0 --port $REST_API_PORT --reload
