from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, field_validator
from typing import Union, Iterable

import logging
from .abstract_cassandra_client import AbstractCassandraClient
from ..wiki_models.models import PageInformation, ActiveUser


class WikiCassandraClient(AbstractCassandraClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        logging.info("`WikiCassandraClient` has initialized successfully")

    def get_unique_domains(self) -> list[str]:
        query = f"SELECT domain FROM {self.keyspace}.unique_domains;"

        q_result = self.execute(query).all()
        return [row.domain for row in q_result]

    def get_user_page_ids(self, user_id: int) -> list[int]:
        query = f"SELECT page_id FROM {self.keyspace}.user_pages WHERE user_id = {user_id};"
        q_result = self.execute(query).all()
        return [row.page_id for row in q_result]

    def get_page_information(self, page_id: int) -> Union[PageInformation, None]:
        query = f"SELECT * FROM {self.keyspace}.page_information WHERE page_id = {page_id};"
        q_result = self.execute(query).all()
        if not q_result:
            return None

        return PageInformation(page_id=q_result[0].page_id, uri=q_result[0].uri, title=q_result[0].title)

    def get_num_pages(self, domain: str) -> int:
        query = f"SELECT num_pages FROM {self.keyspace}.domain_pages WHERE domain = '{domain}';"
        q_result = self.execute(query).all()
        if not q_result:
            return 0
        return q_result[0].num_pages

    def get_active_users_by_date(self, date: str) -> Iterable[ActiveUser]:
        query = f"SELECT user_id, user_name, num_created_pages FROM {self.keyspace}.active_users_by_date WHERE date = '{date}';"
        q_result = self.execute(query).all()
        return (ActiveUser(user_id=row.user_id, user_name=row.user_name, num_created_pages=row.num_created_pages) for row in q_result)


if __name__ == "__main__":
    raise NotImplementedError("This module is not intended to be run directly.")
