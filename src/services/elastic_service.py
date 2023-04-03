"""Helper module for elasticsearch data."""

from uuid import UUID

import backoff
from elasticsearch import (
    AsyncElasticsearch,
    ConnectionError,
    NotFoundError,
    TransportError,
)

from db.data_storage_interface import DataStorageInterface


class ElasticSearvice(DataStorageInterface):
    def __init__(self, storage_client: AsyncElasticsearch):
        self._es = storage_client

    @backoff.on_exception(backoff.expo, (ConnectionError, TransportError))
    async def get_data_by_id(self, *args, **kwargs) -> dict:
        index = kwargs.get('index')
        data_id: UUID = kwargs.get('id')
        try:
            doc = await self._es.get(index=index, id=data_id)
        except NotFoundError:
            return {}
        return doc['_source']

    @backoff.on_exception(backoff.expo, (ConnectionError, TransportError))
    async def search_data(self, *args, **kwargs) -> list:
        query_body = kwargs.get('query_body')
        index = kwargs.get('index')
        try:
            doc = await self._es.search(body=query_body, index=index)
        except NotFoundError:
            return []
        return [data['_source'] for data in doc['hits']['hits']]
