from dataclasses import dataclass
from functools import lru_cache
from typing import Optional, Union

import orjson
from elasticsearch import NotFoundError
from pydantic import BaseModel, Field

from models.film import Film
from models.genre import Genre
from models.person import PersonBase

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут


def orjson_dumps(v, *, default):
    return orjson.dumps(v, default=default).decode()


class OrjsonMixin(BaseModel):
    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps


class RetrieveDataMixin:
    """Mixin class for retrieving data from a databases."""

    async def get_by_id(self, data_id: str) -> Film | Genre | PersonBase:
        data = await self._data_from_cache(data_id)
        if not data:
            data = await self._get_data_from_elastic(data_id)
            if not data:
                return None
            await self._put_data_to_cache(data)

        return data

    async def get_genres_list(self, *args, **kwargs):
        try:
            result = await self.elastic.search(
                index="genres",
                body={"query": {"match_all": {}}},
                size=100,
            )
        except NotFoundError:
            return None
        return [
            self.model(**item['_source']) for item in result['hits']['hits']
        ]

    async def _get_data_from_elastic(
        self, data_id: str
    ) -> Film | Genre | list[Genre] | PersonBase:
        try:
            doc = await self.elastic.get(index=self.elastic_index, id=data_id)
        except NotFoundError:
            return None
        return self.model(**doc['_source'])

    async def _data_from_cache(
        self, data_id: str | None = None
    ) -> Film | Genre | PersonBase:
        data = await self.redis.get(str(data_id))
        if not data:
            return None

        data = self.model.parse_raw(data)
        return data

    async def _put_data_to_cache(
        self, data: Film | Genre | list[Genre | Film] | PersonBase
    ) -> Film | Genre:
        await self.redis.set(
            str(data.uuid), data.json(), FILM_CACHE_EXPIRE_IN_SECONDS
        )
