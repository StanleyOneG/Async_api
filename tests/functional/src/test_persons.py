import logging
from http import HTTPStatus

import pytest
from functional.conftest import FILM_UUID, persons_names, persons_uuids
from functional.settings import test_settings

pytestmark = pytest.mark.asyncio

logger = logging.getLogger('test_persons')


@pytestmark
async def test_get_person(
        es_write_data,
        make_person_get_request,
        persons_data,
):
    await es_write_data(persons_data, test_settings.es_persons_index)
    response = await make_person_get_request()

    body = await response.json()
    status = response.status

    assert status == HTTPStatus.OK
    assert body.get('uuid') == persons_uuids[3]
    assert body.get('full_name') == persons_names[3]


@pytestmark
async def test_get_persons_film(es_write_data, make_film_request, film_data):
    await es_write_data(film_data, test_settings.es_movies_index)
    response = await make_film_request()

    body = await response.json()
    status = response.status

    assert status == HTTPStatus.OK
    assert body[0].get('uuid') == FILM_UUID
    assert body[0].get('title') == 'Terminator'


@pytestmark
async def test_search_person(make_film_search_request):
    response = await make_film_search_request(
        'Ivan', through_person_endpoint=True
    )

    body = await response.json()
    status = response.status

    assert status == HTTPStatus.OK
    assert body[0].get('full_name') == 'Ivan Ivanov'
