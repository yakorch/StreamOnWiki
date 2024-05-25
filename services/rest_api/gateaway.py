import fastapi

from services.wiki_models.models import PageInformation, ActiveUser
from .logging_config import *
from .date_iterator import date_range
from collections import Counter


from typing import Union

import os
from services.cassandra_communication.wiki_cassandra_client import WikiCassandraClient

wiki_cassandra_client = WikiCassandraClient(
    host=os.environ["CASSANDRA_HOST"], port=os.environ["CASSANDRA_PORT"], keyspace=os.environ["CASSANDRA_KEYSPACE"]
)

app = fastapi.FastAPI(title="Wikipedia Pages Info")


@app.get("/")
async def root():
    return {"Goodbye": "World"}


### Category A -->


### Category B -->


@app.get("/queries/domains/updated")
async def get_updated_domains() -> list[str]:
    """
    Returns the list of domains, for which the pages have been created.
    """
    return wiki_cassandra_client.get_unique_domains()


@app.get("/queries/users/{user_id}/created-pages")
async def get_pages(user_id: int) -> list[int]:
    """
    Returns the page ids, created by the user with the given `user_id`.
    """
    return wiki_cassandra_client.get_user_page_ids(user_id)


@app.get("/queries/domains/{domain}/num-created-pages")
async def get_num_articles(domain: str) -> int:
    """
    Returns the number of pages created for the given `domain`.
    """
    return wiki_cassandra_client.get_num_pages(domain)


@app.get("/queries/pages/{page_id}", response_model=PageInformation)
async def get_page(page_id: int) -> Union[PageInformation, fastapi.Response]:
    """
    Returns the information about the page for the given `page_id`.
    """
    page_info = wiki_cassandra_client.get_page_information(page_id)
    if page_info is None:
        return fastapi.Response(status_code=404)
    return page_info


DATE_REGEX = r"^\d{4}-\d{2}-\d{2}$"


@app.get("/queries/users/active")
async def get_active_users(
    start_date: str = fastapi.Query(..., regex=DATE_REGEX), end_date: str = fastapi.Query(..., regex=DATE_REGEX)
) -> list[ActiveUser]:
    """
    Returns the list of users that have created at least one page in the specified time period.
    """
    counter = Counter()
    for date in date_range(start_date, end_date):
        active_users = wiki_cassandra_client.get_active_users_by_date(str(date))
        for user in active_users:
            counter[(user.user_id, user.user_name)] += user.num_created_pages

    return [ActiveUser(user_id=user[0], user_name=user[1], num_created_pages=num_created_pages) for user, num_created_pages in counter.items()]
