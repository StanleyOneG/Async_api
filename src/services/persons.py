from functools import lru_cache

from fastapi import Depends

from db.data_storage_interface import DataStorageInterface
from db.storage import get_storage
from services.base_elastic_services import BaseElasticService
from services.base_service import MovieService


class ElasticPersonsService(BaseElasticService, MovieService):
    """Represents a persons collection from storage."""

    def __init__(self, storage: DataStorageInterface) -> None:
        self.storage = storage
        self.elastic_index = 'persons'


@lru_cache()
def get_elastic_persons_service(
    storage: DataStorageInterface = Depends(get_storage),
):
    return ElasticPersonsService(storage)
