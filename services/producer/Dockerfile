FROM python:3.9-slim

LABEL authors="mrkorch"

RUN apt-get update
RUN pip install --upgrade pip

WORKDIR /opt/app

COPY requirements.txt .
RUN pip install -r requirements.txt

WORKDIR /opt
ENTRYPOINT python -m app.listen_wikipedia_events
