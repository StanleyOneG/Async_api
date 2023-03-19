from functools import lru_cache

from fastapi import Depends

from db.elastic import get_elastic
from models.elastic_service import AbstractElasticService
from models.person import PersonWithFilms, PersonBase
from api.v1.utils import PaginateQueryParams


class PersonService:
    """Represent a persons collection on API side."""

    def __init__(
        self,
        elastic: AbstractElasticService,
        elastic_index: str,
        model: PersonWithFilms,
    ):
        self.elastic = elastic
        self.elastic_index = elastic_index
        self.model = model


    async def get_by_id(
        self, data_id: str, model: PersonWithFilms | PersonBase
    ):
        return await self.elastic.get_data_from_elastic(
            data_id, model, self.elastic_index
        )

    async def get_persons_search(
        self,
        query: str,
        paginate_query_params: PaginateQueryParams,
    ) -> list[PersonWithFilms]:
        return await self.elastic.search_data_in_elastic(
            query, paginate_query_params, self.elastic_index
        )


@lru_cache()
def get_person_service(
    elastic: AbstractElasticService = Depends(get_elastic),
) -> PersonService:
    return PersonService(
        elastic=elastic,
        model=PersonWithFilms,
        elastic_index='persons',
    )
