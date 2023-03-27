import random
from faker import Faker
import uuid
import logging
import pytest
from functional.settings import test_settings
from functional.conftest import persons_uuids, persons_names
import pytest
from functional.utils.helpers import fake
from functional.settings import test_settings

logger = logging.getLogger('test_persons')


@pytest.mark.asyncio
async def test_get_person(
    es_write_data,
    make_film_get_request,
    persons_data,
):
    await es_write_data(persons_data, test_settings.es_persons_index)
    response = await make_film_get_request()
    body = await response.json()
    status = response.status

    assert status == 200
    assert body.get('uuid') == persons_uuids[3]
    assert body.get('full_name') == persons_names[3]


@pytest.mark.asyncio
async def test_get_persons_film(es_write_data, make_film_request, film_data):
    await es_write_data(film_data, test_settings.es_movies_index)
    response = await make_film_request()
    body = await response.json()
    status = response.status

    assert status == 200
    assert body[0].get('uuid') == 'b92ef010-5e4c-4fd0-99d6-41b6456272cd'
    assert body[0].get('title') == 'Terminator'


@pytest.mark.asyncio
async def test_search_person(make_film_search_request):
    response = await make_film_search_request('Ivan')
    body = await response.json()
    status = response.status

    assert status == 200
    assert body[0].get('full_name') == 'Ivan Ivanov'


persons_uuids = [fake.uuid4() for _ in range(10)]
persons_names = [fake.name() for _ in range(10)]


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
                'uuid': '56b541ab-4d66-4021-8708-397762bff2d4',
                'full_name': 'Ivan Ivanov',
                'film_work_ids': ['b92ef010-5e4c-4fd0-99d6-41b6456272cd'],
            }
        ]
    )
    return es_data


@pytest.fixture
def film_data():
    es_data = [
        {
            'uuid': 'b92ef010-5e4c-4fd0-99d6-41b6456272cd',
            'imdb_rating': 8.5,
            'genre': [
                {'uuid': str(fake.uuid4()), 'name': 'Sci-Fi'},
            ],
            'title': 'Terminator',
            'description': 'New World',
            'directors': [{'uuid': '1234', 'full_name': 'John Doe'}],
            'actors_names': ['Ivan Ivanov', 'Bob'],
            'writers_names': ['Ben', 'Howard'],
            'actors': [
                {
                    'uuid': '56b541ab-4d66-4021-8708-397762bff2d4',
                    'full_name': 'Ivan Ivanov',
                },
                {'uuid': '222', 'full_name': 'Bob'},
            ],
            'writers': [
                {'uuid': '333', 'full_name': 'Ben'},
                {'uuid': '444', 'full_name': 'Howard'},
            ],
        }
    ]
    return es_data


@pytest.fixture
def make_get_request(get_client_session):
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
        uuid_to_get = '56b541ab-4d66-4021-8708-397762bff2d4'
        url = test_settings.service_url + f'/api/v1/persons/{uuid_to_get}/film'
        async for session in get_client_session:
            response = await session.get(url)
            return response

    return inner


@pytest.fixture
def make_search_request(get_client_session):
    async def inner(data_to_search):
        params = {
            'query': data_to_search,
        }
        url = test_settings.service_url + '/api/v1/persons/search'
        async for session in get_client_session:
            response = await session.get(url, params=params)
            return response

    return inner


@pytest.mark.asyncio
async def test_get_person(
    es_write_data,
    make_get_request,
    persons_data,
):

    await es_write_data(persons_data, test_settings.es_persons_index)
    response = await make_get_request()
    body = await response.json()
    status = response.status

    assert status == 200
    assert body.get('uuid') == persons_uuids[3]
    assert body.get('full_name') == persons_names[3]


@pytest.mark.asyncio
async def test_get_persons_film(es_write_data, make_film_request, film_data):
    await es_write_data(film_data, test_settings.es_movies_index)
    response = await make_film_request()
    body = await response.json()
    status = response.status

    assert status == 200
    assert body[0].get('uuid') == 'b92ef010-5e4c-4fd0-99d6-41b6456272cd'
    assert body[0].get('title') == 'Terminator'


@pytest.mark.asyncio
async def test_search_person(make_search_request):
    response = await make_search_request('Ivan')
    body = await response.json()
    status = response.status

    assert status == 200
    assert body[0].get('full_name') == 'Ivan Ivanov'
