from functools import lru_cache

from fastapi import Depends

from db.elastic import get_elastic
from models.genre import Genre
from models.elastic_service import AbstractElasticService


class GenreService:
    def __init__(
        self,
        elastic: AbstractElasticService,
        elastic_index: str,
        model: Genre,
    ):
        self.elastic = elastic
        self.elastic_index = elastic_index
        self.model = model

    async def get_by_id(self, data_id: str, model: Genre):
        return await self.elastic.get_data_from_elastic(
            data_id, model, self.elastic_index
        )

    async def get_list(
        self,
    ):
        return await self.elastic.get_list_from_elastic(
            elastic_index=self.elastic_index
        )


@lru_cache()
def get_genre_service(
    elastic: AbstractElasticService = Depends(get_elastic),
) -> GenreService:
    return GenreService(
        elastic=elastic,
        model=Genre,
        elastic_index='genres',
    )
