import logging
import uuid

import aiohttp
import pytest
from tests.functional.settings import test_settings

logger = logging.getLogger('tests')


@pytest.fixture
def es_data() -> list[dict]:
    es_data = [
        {
            'uuid': str(uuid.uuid4()),
            'imdb_rating': 8.5,
            'genre': [
                {'uuid': '1234', 'name': 'Sci-Fi'},
            ],
            'title': 'The Star',
            'description': 'New World',
            'directors': [{'uuid': '1234', 'full_name': 'John Doe'}],
            'actors_names': ['Ann', 'Bob'],
            'writers_names': ['Ben', 'Howard'],
            'actors': [
                {'uuid': '111', 'full_name': 'Ann'},
                {'uuid': '222', 'full_name': 'Bob'},
            ],
            'writers': [
                {'uuid': '333', 'full_name': 'Ben'},
                {'uuid': '444', 'full_name': 'Howard'},
            ],
        }
        for _ in range(60)
    ]
    return es_data


@pytest.fixture
def make_get_request(get_client_session):
    async def inner(query_data: dict):
        url = test_settings.service_url + '/api/v1/films/search'
        async for session in get_client_session:
            response = await session.get(url, params=query_data)
            return response

    return inner


@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        (
            {'query': 'The Star'},
            {'status': 200, 'length': 50},
        ),
        (
            {'query': 'Mashed potato'},
            {'status': 200, 'length': 0},
        ),
    ],
)
@pytest.mark.asyncio
async def test_search(
    es_write_data,
    make_get_request,
    es_data: list[dict],
    query_data: dict,
    expected_answer: dict,
):

    await es_write_data(es_data)
    response = await make_get_request(query_data)
    length = await response.json()
    headers = response.headers
    status = response.status

    assert status == expected_answer['status']
    assert len(length) == expected_answer['length']
