from functools import lru_cache
from uuid import UUID

from fastapi import Depends

from api.v1.utils import PaginateQueryParams
from db.data_storage_interface import DataStorageInterface
from db.storage import get_storage
from models.query_constructor import QueryConstructor
from services.base_service import MovieService


class ElasticFilmService(MovieService):
    """Represent a films collection from storage."""

    def __init__(self, storage: DataStorageInterface) -> None:
        self.storage = storage
        self.elastic_index = 'movies'

    async def get_by_id(self, id: UUID):
        film = await self.storage.get_data_by_id(
            index=self.elastic_index,
            id=id,
        )
        return film

    async def search_data(
        self,
        parameters: PaginateQueryParams,
        query: str = None,
        sort: str = None,
        filter: UUID = None,
    ) -> list:
        if filter is not None:
            return await self.get_films(
                parameters=parameters,
                sort=sort,
                filter_genre=filter,
            )
        query_constructor = QueryConstructor(
            sort=sort,
            query=query,
            paginate_query_params=parameters,
        )
        query_body = query_constructor.construct_query(self.elastic_index)
        return await self.storage.search_data(
            query_body=query_body,
            index=self.elastic_index,
        )

    async def get_films(
        self,
        parameters: PaginateQueryParams,
        filter_genre: UUID,
        sort: str = None,
    ):
        query_constructor = QueryConstructor(
            paginate_query_params=parameters,
            sort=sort,
            filter_genre=filter_genre,
        )
        query_body = query_constructor.construct_films_list_query()
        return await self.storage.search_data(
            body=query_body,
            index=self.elastic_index,
        )


@lru_cache()
def get_elastic_film_service(
    storage: DataStorageInterface = Depends(get_storage),
):
    return ElasticFilmService(storage)
