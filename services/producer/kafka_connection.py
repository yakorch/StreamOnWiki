import json
from kafka import KafkaProducer
import os


def connect_as_producer():
    bootstrap_servers = os.environ["BOOTSTRAP_SERVERS"]
    return KafkaProducer(bootstrap_servers=bootstrap_servers, value_serializer=lambda v: json.dumps(v).encode("utf-8"), retries=5)
