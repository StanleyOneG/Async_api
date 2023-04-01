import logging

import pytest
from functional.conftest import genres_names, genres_uuids
from functional.settings import test_settings

pytestmark = pytest.mark.asyncio

logger = logging.getLogger('test_genres')


@pytestmark
async def test_genres_id(
        es_write_data,
        make_genre_id_request,
        genres_data,
):
    await es_write_data(genres_data, test_settings.es_genres_index)
    response = await make_genre_id_request()

    body = await response.json()
    status = response.status

    assert status == 200
    assert body.get('uuid') == genres_uuids[3]
    assert body.get('name') == genres_names[3]


@pytestmark
async def test_genres(
        es_write_data,
        make_genres_request,
        genres_data,
):
    await es_write_data(genres_data, test_settings.es_genres_index)
    response = await make_genres_request()

    body = await response.json()
    body_names = [genre['name'] for genre in body]
    body_uuids = [genre['uuid'] for genre in body]
    status = response.status

    for genre_uuid in genres_uuids:
        assert genre_uuid in body_uuids
    for genre_name in genres_names:
        assert genre_name in body_names
    assert len(body) == len(genres_data)
    assert status == 200
