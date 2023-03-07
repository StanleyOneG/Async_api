from dataclasses import dataclass
from functools import lru_cache

import orjson
from elasticsearch import NotFoundError
from pydantic import BaseModel

from models.film import Film
from models.genre_model import GenreModel

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут


def orjson_dumps(v, *, default):
    return orjson.dumps(v, default=default).decode()


class OrjsonMixin(BaseModel):
    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps


class RetrieveDataMixin:
    """Mixin class for retrieving data from a databases."""

    async def get_by_id(self, data_id: str) -> Film | GenreModel:
        data = await self._data_from_cache(data_id)
        if not data:
            data = await self._get_data_from_elastic(data_id)
            if not data:
                return None
            await self._put_data_to_cache(data)

        return data

    async def _get_data_from_elastic(self, data_id: str) -> Film | GenreModel:
        try:
            doc = await self.elastic.get(self.elastic_index, data_id)
        except NotFoundError:
            return None
        return self.model(**doc['_source'])

    async def _data_from_cache(self, data_id: str) -> Film | GenreModel:
        data = await self.redis.get(data_id)
        if not data:
            return None

        data = self.model.parse_raw(data)
        return data

    async def _put_data_to_cache(
        self, data: Film | GenreModel
    ) -> Film | GenreModel:
        await self.redis.set(
            data.id, data.json(), FILM_CACHE_EXPIRE_IN_SECONDS
        )
