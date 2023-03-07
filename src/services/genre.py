import dataclasses
from functools import lru_cache
from elasticsearch import AsyncElasticsearch

from redis import Redis
from db.elastic import get_elastic
from db.redis import get_redis
from models.film import Film
from models.genre_model import GenreModel
from models.models_mixins import RetrieveDataMixin
from fastapi import Depends


@dataclasses.dataclass
class GenreService(RetrieveDataMixin):

    redis: Redis
    elastic: AsyncElasticsearch
    model: Film | GenreModel
    elastic_index: str


@lru_cache()
def get_genre_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> GenreService:
    return GenreService(redis, elastic, GenreModel, 'genre')
