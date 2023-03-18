import dataclasses
from functools import lru_cache

from elasticsearch import AsyncElasticsearch
from fastapi import Depends
from redis import Redis

from db.elastic import get_elastic
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
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> GenreService:
    return GenreService(
        elastic=elastic,
        model=Genre,
        elastic_index='genres'
    )
