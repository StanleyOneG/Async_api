from functools import lru_cache
from uuid import UUID

from fastapi import Depends

from models.film import Film
from api.v1.utils import PaginateQueryParams
from db.data_storage_interface import DataStorageInterface
from services.base_service import MovieService
from db.storage import get_storage
from models.query_constructor import QueryConstructor
from services.elastic_service import ElasticSearvice


class ElasticFilmService(MovieService):
    """Represent a films collection on API side."""

    def __init__(self, storage: DataStorageInterface) -> None:
        self.storage = storage
        self.elastic_index = 'movies'
        self.elastic_model = Film

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
        **kwargs,
    ) -> list:
        print(f'FROM CALL SEARCH DATA ------------- {self.storage}')
        if 'sort' and 'filter' in kwargs:
            return await self.get_films(
                parameters=parameters,
                sort=kwargs['sort'],
                filter_genre=kwargs['filter'],
            )
        query_constructor = QueryConstructor(
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
        sort: str,
        filter_genre: UUID,
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
    print(f'CALL ELASTICFILMSERVICE ------------------ {storage}')
    return ElasticFilmService(storage)
