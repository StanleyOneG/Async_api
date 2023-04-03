from functools import lru_cache
from uuid import UUID

from fastapi import Depends

from api.v1.utils import PaginateQueryParams
from db.data_storage_interface import DataStorageInterface
from db.storage import get_storage
from models.query_constructor import QueryConstructor
from services.base_service import MovieService


class ElasticPersonsService(MovieService):
    """Represents a persons collection from storage."""

    def __init__(self, storage: DataStorageInterface):
        self.storage = storage
        self.elastic_index = 'persons'

    async def get_by_id(self, id: UUID) -> dict:
        person = await self.storage.get_data_by_id(
            index=self.elastic_index,
            id=id,
        )
        return person

    async def search_data(
        self,
        parameters: PaginateQueryParams,
        query: str = None,
        sort: str = None,
        filter: UUID = None,
    ) -> list:
        query_constructor = QueryConstructor(
            query=query,
            sort=sort,
            paginate_query_params=parameters,
        )
        query_body = query_constructor.construct_query(self.elastic_index)
        return await self.storage.search_data(
            query_body=query_body,
            index=self.elastic_index,
        )


@lru_cache()
def get_elastic_persons_service(
    storage: DataStorageInterface = Depends(get_storage),
):
    return ElasticPersonsService(storage)
