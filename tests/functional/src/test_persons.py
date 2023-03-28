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
