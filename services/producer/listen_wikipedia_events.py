import json
import requests
import time
import os

import logging

logging.basicConfig(level=logging.INFO, format=" %(asctime)s - %(levelname)s - %(message)s")

from .kafka_connection import connect_as_producer

producer = connect_as_producer()

_WIKI_EVENTS_URL = "https://stream.wikimedia.org/v2/stream/page-create"
_WIKI_TOPIC = os.environ["WIKI_EVENTS_TOPIC"]


def send_to_kafka():
    while True:
        try:
            response = requests.get(_WIKI_EVENTS_URL, stream=True)
            for line in response.iter_lines():
                if not (line and line.startswith(b"data:")):
                    continue

                json_data = line[len("data: ") :]
                event = json.loads(json_data.decode("utf-8"))

                meta = event.get("meta", {})
                domain = meta.get("domain")
                uri = meta.get("uri")

                performer = event.get("performer", {})
                user_is_bot = performer.get("user_is_bot")
                user_id = performer.get("user_id")
                user_name = performer.get("user_text")

                title = event.get("page_title")
                page_id = event.get("page_id")
                dt = event.get("dt")

                necessary_fields = (domain, uri, user_is_bot in (False, True), user_id, user_name, title, page_id, dt)
                if not all(necessary_fields):
                    logging.debug(f"Missing required fields from {event}. \n Parsed: {necessary_fields}.")
                    continue

                clean_event = {
                    "domain": domain,
                    "uri": uri,
                    "user_is_bot": user_is_bot,
                    "user_id": user_id,
                    "user_name": user_name,
                    "title": title,
                    "page_id": page_id,
                    "dt": dt,
                }

                producer.send(_WIKI_TOPIC, value=clean_event)
                logging.debug(f"Sent: {clean_event}")

        except requests.exceptions.RequestException as e:
            logging.error(f"Request exception: {e}")
            time.sleep(2)
        except Exception as e:
            logging.error(f"Unexpected exception: {e}")
            time.sleep(1)


if __name__ == "__main__":
    send_to_kafka()
