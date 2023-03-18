"""Helper module for elasticsearch data."""

from elasticsearch import AsyncElasticsearch, NotFoundError
from abc import ABC, abstractmethod
from models.film import Film, FilmBase

from models.person import PersonWithFilms, PersonBase
from models.genre import Genre
from models.query_constructor import QueryConstructor


class AbstractElasticService(ABC):
    @abstractmethod
    async def get_data_from_elastic(
        self,
        data_id: str,
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
        page: int,
        size: int,
        elastic_index: str,
    ):
        pass


class ElasticService(AbstractElasticService):

    def __init__(self, elastic: AsyncElasticsearch) -> None:
        self.elastic = elastic

    async def get_data_from_elastic(
        self,
        data_id: str,
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
        page: int,
        size: int,
        elastic_index: str,
    ):
        call_method = {
            'persons': self.search_persons,
            'movies': self.search_films,
        }
        return await call_method[elastic_index](query, page, size)

    async def get_list_from_elastic(
        self,
        elastic_index: str,
        **kwargs,
    ):
        if elastic_index == 'genres':
            return await self.get_genres_list()
        page = kwargs['page']
        size = kwargs['size']
        sort = kwargs['sort']
        filter_genre = kwargs['filter_genre']
        return await self.get_films_list(
            sort=sort,
            page=page,
            size=size,
            filter_genre=filter_genre,
        )

    async def search_films(
        self,
        query: str,
        page: int,
        size: int,
    ):
        query_constructor = QueryConstructor(query=query, page=page, size=size)
        query_body = query_constructor.construct_query('movies')
        try:
            doc = await self.elastic.search(body=query_body, index='movies')
        except NotFoundError:
            return []
        return [FilmBase(**movie['_source']) for movie in doc['hits']['hits']]

    async def search_persons(
        self,
        query: str,
        page: int,
        size: int,
    ) -> list[PersonWithFilms] | list:
        if not query:
            return None
        query_constructor = QueryConstructor(query=query, page=page, size=size)
        query_body = query_constructor.construct_query('persons')
        try:
            doc = await self.elastic.search(
                body=query_body, index=self.elastic_index
            )
        except NotFoundError:
            return []
        return [
            PersonWithFilms(**person['_source'])
            for person in doc['hits']['hits']
        ]

    async def get_genres_list(self):
        try:
            result = await self.elastic.search(
                index="genres",
                body={"query": {"match_all": {}}},
                size=100,
            )
        except NotFoundError:
            return None
        return [Genre(**item['_source']) for item in result['hits']['hits']]

    async def get_films_list(
        self,
        sort,
        page,
        size,
        filter_genre,
    ) -> list[FilmBase]:
        query_constructor = QueryConstructor(
            page=page,
            size=size,
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
