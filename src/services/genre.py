from functools import lru_cache

from fastapi import Depends

from db.data_storage_interface import DataStorageInterface
from db.storage import get_storage
from services.base_elastic_services import BaseElasticService
from services.base_service import MovieService


class ElasticGenresService(BaseElasticService, MovieService):
    """Represents a genres collection from storage."""

    def __init__(self, storage: DataStorageInterface) -> None:
        self.storage = storage
        self.elastic_index = 'genres'


@lru_cache()
def get_elastic_genres_service(
    storage: DataStorageInterface = Depends(get_storage),
):
    return ElasticGenresService(storage)
