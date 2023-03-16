import dataclasses
from functools import lru_cache

from elasticsearch import AsyncElasticsearch
from fastapi import Depends
from redis import Redis

from db.elastic import get_elastic
from db.redis import get_redis
from models.genre import Genre
from models.models_mixins import RetrieveDataMixin


@dataclasses.dataclass
class GenreService(RetrieveDataMixin):

    redis: Redis
    elastic: AsyncElasticsearch
    model: Genre
    elastic_index: str


@lru_cache()
def get_genre_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> GenreService:
    return GenreService(
        redis=redis, elastic=elastic, model=Genre, elastic_index='genres'
    )
