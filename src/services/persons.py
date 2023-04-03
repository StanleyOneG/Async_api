from functools import lru_cache
from uuid import UUID

from fastapi import Depends
from services.base_service import MovieService
from db.data_storage_interface import DataStorageInterface
from db.storage import get_storage
from api.v1.utils import PaginateQueryParams
from models.query_constructor import QueryConstructor


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
        parameters: PaginateQueryParams = None,
        query: str = None,
        sort: str = None,
        filter: UUID = None,
    ) -> list:
        query_constructor = QueryConstructor(
            query=query,
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


# class PersonService:
#     """Represent a persons collection on API side."""

#     def __init__(
#         self,
#         elastic: AbstractElasticService,
#         elastic_index: str,
#         model: PersonWithFilms,
#     ):
#         self.elastic = elastic
#         self.elastic_index = elastic_index
#         self.model = model

#     async def get_by_id(
#         self, data_id: UUID, model: PersonWithFilms | PersonBase
#     ):
#         return await self.elastic.get_data_from_elastic(
#             data_id, model, self.elastic_index
#         )

#     async def get_persons_search(
#         self,
#         query: str,
#         paginate_query_params: PaginateQueryParams,
#     ) -> list[PersonWithFilms]:
#         return await self.elastic.search_data_in_elastic(
#             query, paginate_query_params, self.elastic_index
#         )


# @lru_cache()
# def get_person_service(
#     elastic: AbstractElasticService = Depends(get_elastic),
# ) -> PersonService:
#     return PersonService(
#         elastic=elastic,
#         model=PersonWithFilms,
#         elastic_index='persons',
#     )
