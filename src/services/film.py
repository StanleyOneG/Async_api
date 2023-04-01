from functools import lru_cache
from uuid import UUID

from fastapi import Depends

from db.elastic import get_elastic
from models.film import Film, FilmBase
from services.elastic_service import AbstractElasticService
from api.v1.utils import PaginateQueryParams


class FilmService:
    """Represent a films collection on API side."""

    def __init__(
        self,
        elastic: AbstractElasticService,
        elastic_index: str,
    ) -> None:
        self.elastic = elastic
        self.elastic_index = elastic_index

    async def get_by_id(self, film_id: UUID, model: FilmBase | Film):
        return await self.elastic.get_data_from_elastic(
            film_id, model, self.elastic_index
        )

    async def get_films_search(
        self,
        query: str,
        paginate_query_params: PaginateQueryParams,
    ) -> list[FilmBase]:
        return await self.elastic.search_data_in_elastic(
            query,
            paginate_query_params,
            self.elastic_index,
        )

    async def get_films(
        self,
        paginate_query_params: PaginateQueryParams,
        sort: str,
        filter_genre: UUID,
    ):
        return await self.elastic.get_list_from_elastic(
            elastic_index=self.elastic_index,
            paginate_query_params=paginate_query_params,
            sort=sort,
            filter_genre=filter_genre,
        )


@lru_cache()
def get_film_service(
    elastic: AbstractElasticService = Depends(get_elastic),
) -> FilmService:
    return FilmService(elastic=elastic, elastic_index='movies')
