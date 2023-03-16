from dataclasses import dataclass
from functools import lru_cache

from elasticsearch import AsyncElasticsearch
from fastapi import Depends
from redis import Redis

from db.elastic import get_elastic
from db.redis import get_redis
from models.models_mixins import RetrieveDataMixin
from models.person import PersonWithFilms


@dataclass
class PersonService(RetrieveDataMixin):
    """Represent a persons collection on API side."""

    redis: Redis
    elastic: AsyncElasticsearch
    model: PersonWithFilms
    elastic_index: str


@lru_cache()
def get_person_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonService:
    return PersonService(
        redis=redis,
        elastic=elastic,
        model=PersonWithFilms,
        elastic_index='persons',
    )
