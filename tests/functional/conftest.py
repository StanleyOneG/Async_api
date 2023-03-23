from dataclasses import dataclass
import json
from typing import Generator
import backoff
from elasticsearch import AsyncElasticsearch, Elasticsearch, TransportError
from pydantic import BaseModel, FilePath
import pytest
from redis import Redis
from functional.settings import test_settings, test_indexes, index_names
import logging


logger = logging.getLogger('tests')


class ElasticIndex(BaseModel):
    """Class for elasticsearch index settings validation."""

    settings: dict
    mappings: dict


@backoff.on_exception(backoff.expo, (ConnectionError, TransportError))
async def create_index(
    es_index: str,
    es_schema: FilePath,
    es_client: AsyncElasticsearch,
) -> None:
    """Create Elasticsearch index if it does not exist."""
    with open(es_schema, 'r') as file:
        data = json.load(
            file,
        )

    index = ElasticIndex.parse_raw(str(data).replace("'", '"'))

    try:
        await es_client.indices.create(
            index=es_index,
            settings=index.settings,
            mappings=index.mappings,
        )
    except TransportError as transport_error:
        logger.error(transport_error)


def get_es_bulk_query(
    data: list[dict], index: str, id_field: str
) -> list[dict]:
    bulk_query = []
    for row in data:
        bulk_query.extend(
            [
                json.dumps(
                    {
                        'index': {
                            '_index': index,
                            '_id': row[id_field],
                        }
                    }
                ),
                json.dumps(row),
            ]
        )
    return bulk_query


@pytest.fixture(autouse=True, scope='session')
def redis_client() -> Generator[Redis, None, None]:
    redis_client = Redis(host=test_settings.redis_host, port=6379, db=0)
    yield
    redis_client.flushall()
    redis_client.close()


@pytest.fixture(scope='session')
async def es_client(request) -> Generator[AsyncElasticsearch, None, None]:
    es_client = AsyncElasticsearch(
        test_settings.es_host,
        validate_cert=False,
        use_ssl=False,
        http_auth=(test_settings.es_user, test_settings.es_password),
    )
    async for index_name, index_map in test_indexes:
        if not await es_client.indices.exists(index=index_name):
            await create_index(index_name, index_map, es_client)
    yield es_client
    await es_client.close()


@pytest.fixture(scope='module', autouse=True)
def cleanup(request):
    def delete_index():
        es_client = Elasticsearch(
            test_settings.es_host,
            validate_cert=False,
            use_ssl=False,
            http_auth=(test_settings.es_user, test_settings.es_password),
        )
        with es_client as client:
            for index_name in index_names:
                if client.indices.exists(index=index_name):
                    client.indices.delete(index=index_name)

    request.addfinalizer(delete_index)


@pytest.fixture
def es_write_data(es_client):
    async def inner(data: list[dict]):
        async for client in es_client:
            bulk_query = get_es_bulk_query(
                data, test_settings.es_movies_index, test_settings.es_id_field
            )
            str_query = '\n'.join(bulk_query) + '\n'
            response = await client.bulk(body=str_query, refresh=True)
            if response['errors']:
                raise Exception('Ошибка записи данных в Elasticsearch')

    return inner
