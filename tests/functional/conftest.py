import json
import logging
from typing import Generator

import aiohttp
import backoff
import pytest
from elasticsearch import AsyncElasticsearch, Elasticsearch, TransportError
from functional.settings import index_names, test_indexes, test_settings
from functional.utils.helpers import fake
from pydantic import BaseModel, FilePath
from redis import Redis

logger = logging.getLogger('tests')

genres_uuids = [fake.uuid4() for _ in range(10)]
genres_names = [fake.genre_name() for _ in range(10)]

persons_uuids = [fake.uuid4() for _ in range(10)]
persons_names = [fake.name() for _ in range(10)]

FILM_UUID = str(fake.uuid4())
PERSON_UUID = str(fake.uuid4())


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


@pytest.fixture(scope='function')
async def get_client_session():
    async with aiohttp.ClientSession() as session:
        yield session


@pytest.fixture()
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
    async def inner(data: list[dict], index: str):
        async for client in es_client:
            bulk_query = get_es_bulk_query(
                data, index, test_settings.es_id_field
            )
            str_query = '\n'.join(bulk_query) + '\n'
            response = await client.bulk(body=str_query, refresh=True)
            if response['errors']:
                raise Exception('Ошибка записи данных в Elasticsearch')

    return inner


@pytest.fixture
def genres_data() -> list[dict]:
    es_data = [
        {
            'uuid': str(genre_uuid),
            'name': genre_name,
        }
        for genre_uuid, genre_name in zip(genres_uuids, genres_names)
    ]
    return es_data


@pytest.fixture
def make_genre_id_request(get_client_session):
    async def inner():
        uuid_to_get = genres_uuids[3]
        url = test_settings.service_url + f'/api/v1/genres/{uuid_to_get}'
        async for session in get_client_session:
            response = await session.get(url)
            return response

    return inner


@pytest.fixture
def make_genres_request(get_client_session):
    async def inner():
        url = test_settings.service_url + '/api/v1/genres/'
        async for session in get_client_session:
            response = await session.get(url)
            return response

    return inner


@pytest.fixture
def persons_data():
    es_data = [
        {
            'uuid': str(person_uuid),
            'full_name': person_name,
            'film_work_ids': [],
        }
        for person_uuid, person_name in zip(persons_uuids, persons_names)
    ]
    es_data.extend(
        [
            {
                'uuid': PERSON_UUID,
                'full_name': 'Ivan Ivanov',
                'film_work_ids': [FILM_UUID],
            }
        ]
    )
    return es_data


@pytest.fixture
def film_data():
    es_data = [
        {
            'uuid': FILM_UUID,
            'imdb_rating': 8.5,
            'genre': [
                {'uuid': str(fake.uuid4()), 'name': 'Sci-Fi'},
            ],
            'title': 'Terminator',
            'description': 'New World',
            'directors': [
                {'uuid': str(fake.uuid4()), 'full_name': 'John Doe'}
            ],
            'actors_names': ['Ivan Ivanov', 'Bob'],
            'writers_names': ['Ben', 'Howard'],
            'actors': [
                {
                    'uuid': PERSON_UUID,
                    'full_name': 'Ivan Ivanov',
                },
                {'uuid': str(fake.uuid4()), 'full_name': 'Bob'},
            ],
            'writers': [
                {'uuid': str(fake.uuid4()), 'full_name': 'Ben'},
                {'uuid': str(fake.uuid4()), 'full_name': 'Howard'},
            ],
        }
    ]
    return es_data


@pytest.fixture
def make_get_request(get_client_session):
    async def inner(**kwargs):
        url = test_settings.service_url + kwargs.get('endpoint_url')
        async for session in get_client_session:
            response = await session.get(url, params=kwargs.get('query_data'))
            return response

    return inner


@pytest.fixture
def make_person_get_request(get_client_session):
    async def inner():
        uuid_to_get = persons_uuids[3]
        url = test_settings.service_url + f'/api/v1/persons/{uuid_to_get}'
        async for session in get_client_session:
            response = await session.get(url)
            return response

    return inner


@pytest.fixture
def make_film_request(get_client_session):
    async def inner():
        uuid_to_get = PERSON_UUID
        url = test_settings.service_url + f'/api/v1/persons/{uuid_to_get}/film'
        async for session in get_client_session:
            response = await session.get(url)
            return response

    return inner


@pytest.fixture
def make_film_search_request(get_client_session):
    async def inner(
        data_to_search: str, through_person_endpoint: bool = False
    ):
        params = {
            'query': data_to_search,
        }
        if through_person_endpoint:
            url = test_settings.service_url + '/api/v1/persons/search'
        else:
            url = test_settings.service_url + '/api/v1/films/search'
        async for session in get_client_session:
            response = await session.get(url, params=params)
            return response

    return inner


@pytest.fixture
def es_movies_data() -> list[dict]:
    es_data = [
        {
            'uuid': str(fake.uuid4()),
            'imdb_rating': 8.5,
            'genre': [
                {'uuid': str(fake.uuid4()), 'name': 'Sci-Fi'},
            ],
            'title': 'The Star',
            'description': 'New World',
            'directors': [
                {'uuid': str(fake.uuid4()), 'full_name': 'John Doe'}
            ],
            'actors_names': ['Ann', 'Bob'],
            'writers_names': ['Ben', 'Howard'],
            'actors': [
                {'uuid': str(fake.uuid4()), 'full_name': 'Ann'},
                {'uuid': str(fake.uuid4()), 'full_name': 'Bob'},
            ],
            'writers': [
                {'uuid': str(fake.uuid4()), 'full_name': 'Ben'},
                {'uuid': str(fake.uuid4()), 'full_name': 'Howard'},
            ],
        }
        for _ in range(60)
    ]
    return es_data
