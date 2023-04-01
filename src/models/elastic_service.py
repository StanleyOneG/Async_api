"""Helper module for elasticsearch data."""

from uuid import UUID
from elasticsearch import (
    AsyncElasticsearch,
    NotFoundError,
    ConnectionError,
    TransportError,
)
from abc import ABC, abstractmethod
from models.film import Film, FilmBase

from models.person import PersonWithFilms, PersonBase
from models.genre import Genre
from models.query_constructor import QueryConstructor
from api.v1.utils import PaginateQueryParams
import backoff


class AbstractElasticService(ABC):
    @abstractmethod
    async def get_data_from_elastic(
        self,
        data_id: UUID,
        model: PersonWithFilms | PersonBase | Genre | Film,
        elastic_index: str,
    ):
        pass

    @abstractmethod
    async def get_list_from_elastic(self, elastic_index: str, **kwargs):
        pass

    @abstractmethod
    async def search_data_in_elastic(
        self,
        query: str,
        paginate_query_params,
        elastic_index: str,
    ):
        pass


class ElasticService(AbstractElasticService):
    def __init__(self, elastic: AsyncElasticsearch) -> None:
        self.elastic = elastic

    @backoff.on_exception(backoff.expo, (ConnectionError, TransportError))
    async def get_data_from_elastic(
        self,
        data_id: UUID,
        model: PersonWithFilms | PersonBase | Genre | Film,
        elastic_index: str,
    ) -> PersonWithFilms | PersonBase | Genre | Film:
        try:
            doc = await self.elastic.get(index=elastic_index, id=data_id)
        except NotFoundError:
            return None
        return model(**doc['_source'])

    async def search_data_in_elastic(
        self,
        query: str,
        paginate_query_params: PaginateQueryParams,
        elastic_index: str,
    ):
        call_method = {
            'persons': self.search_persons,
            'movies': self.search_films,
        }
        return await call_method[elastic_index](query, paginate_query_params)

    async def get_list_from_elastic(
        self,
        elastic_index: str,
        **kwargs,
    ) -> list[Genre] | list[FilmBase] | None:
        if elastic_index == 'genres':
            return await self.get_genres_list()
        paginate_query_params = kwargs['paginate_query_params']
        sort = kwargs['sort']
        filter_genre = kwargs['filter_genre']
        return await self.get_films_list(
            sort=sort,
            paginate_query_params=paginate_query_params,
            filter_genre=filter_genre,
        )

    @backoff.on_exception(backoff.expo, (ConnectionError, TransportError))
    async def search_films(
        self,
        query: str,
        paginate_query_params: PaginateQueryParams,
    ) -> list | list[FilmBase]:
        query_constructor = QueryConstructor(
            query=query, paginate_query_params=paginate_query_params
        )
        query_body = query_constructor.construct_query('movies')
        try:
            doc = await self.elastic.search(body=query_body, index='movies')
        except NotFoundError:
            return []
        return [FilmBase(**movie['_source']) for movie in doc['hits']['hits']]

    @backoff.on_exception(backoff.expo, (ConnectionError, TransportError))
    async def search_persons(
        self,
        query: str,
        paginate_query_params: PaginateQueryParams,
    ) -> list[PersonWithFilms] | list:
        if not query:
            return None
        query_constructor = QueryConstructor(
            query=query, paginate_query_params=paginate_query_params
        )
        query_body = query_constructor.construct_query('persons')
        try:
            doc = await self.elastic.search(body=query_body, index='persons')
        except NotFoundError:
            return []
        return [
            PersonWithFilms(**person['_source'])
            for person in doc['hits']['hits']
        ]

    @backoff.on_exception(backoff.expo, (ConnectionError, TransportError))
    async def get_genres_list(self) -> list[Genre] | None:
        try:
            result = await self.elastic.search(
                index="genres",
                body={"query": {"match_all": {}}},
                size=100,
            )
        except NotFoundError:
            return None
        return [Genre(**item['_source']) for item in result['hits']['hits']]

    @backoff.on_exception(backoff.expo, (ConnectionError, TransportError))
    async def get_films_list(
        self,
        sort,
        paginate_query_params,
        filter_genre,
    ) -> list[FilmBase] | list:
        query_constructor = QueryConstructor(
            paginate_query_params=paginate_query_params,
            sort=sort,
            filter_genre=filter_genre,
        )
        query_body = query_constructor.construct_films_list_query()
        try:
            doc = await self.elastic.search(index='movies', body=query_body)
        except NotFoundError:
            return []
        if doc['hits']['total']['value'] > 0:
            return [
                FilmBase(**movie['_source']) for movie in doc['hits']['hits']
            ]
        return []
