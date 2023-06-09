import logging
import random
from http import HTTPStatus

import pytest
from functional.settings import test_settings

pytestmark = pytest.mark.asyncio

logger = logging.getLogger('tests')


@pytestmark
async def test_film_by_id(es_write_data, es_movies_data, make_get_request):
    await es_write_data(es_movies_data, test_settings.es_movies_index)
    random_film = es_movies_data[random.randrange(0, len(es_movies_data))]
    random_film_id = random_film.get('uuid')
    endpoint_url = '/api/v1/films/' + random_film_id
    response = await make_get_request(endpoint_url=endpoint_url)

    status = response.status
    film_details_response = await response.json()

    assert status == HTTPStatus.OK
    assert film_details_response.get('title') == random_film.get('title')
    assert len(film_details_response.get('actors')) == len(
        random_film.get('actors')
    )


@pytest.mark.parametrize("page_size, page_num, expected_status", [
    (10, 1, HTTPStatus.OK),
    (-10, 1, HTTPStatus.UNPROCESSABLE_ENTITY),
])
async def test_all_films_pagination(make_get_request, page_size, page_num, expected_status):
    endpoint_url = f"/api/v1/films/?page_size={page_size}&page_num={page_num}"
    response = await make_get_request(endpoint_url=endpoint_url)

    body = await response.json()
    status = response.status

    assert status == expected_status
    if expected_status == HTTPStatus.OK:
        assert len(body) == page_size


@pytestmark
async def test_all_films_query_params(make_get_request):
    endpoint_url = '/api/v1/films?page_size=5'
    response = await make_get_request(endpoint_url=endpoint_url)

    length = await response.json()

    assert len(length) == 5


@pytestmark
async def test_non_existing_film(make_get_request):
    endpoint_url = '/api/v1/films/i-will-hack-you'

    response = await make_get_request(endpoint_url=endpoint_url)

    # The value is not a valid uuid
    assert response.status == HTTPStatus.UNPROCESSABLE_ENTITY


@pytest.mark.parametrize("page_size, expected_status", [
    (10, HTTPStatus.OK),
    (-10, HTTPStatus.UNPROCESSABLE_ENTITY),
])
async def test_search_film(make_film_search_request, page_size, expected_status):
    response = await make_film_search_request('The Star', page_size)

    body = await response.json()
    status = response.status

    assert status == expected_status
    if expected_status == HTTPStatus.OK:
        assert body[0].get('title') == 'The Star'
