from functools import lru_cache
from typing import Optional

from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from redis.asyncio import Redis

from db.elastic import get_elastic
from db.redis import get_redis
from models.film import Film, FilmBase


class FilmService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    async def get_films(
            self,
            sort: str,
            size: int,
            page: int,
            filter_genre: str) -> list[FilmBase]:
        films = await self._get_films_from_elastic(
            sort=sort,
            size=size,
            page=page,
            filter_genre=filter_genre
        )
        if not films:
            return []
        return films

    # get_by_id возвращает объект фильма. Он опционален, так как фильм может отсутствовать в базе
    async def get_by_id(self, film_id: str, model: FilmBase | Film) -> Optional[Film | FilmBase]:
        # Пытаемся получить данные из кеша, потому что оно работает быстрее
        if model == FilmBase:
            film = await self._get_film_from_elastic(film_id, model)
            if not film:
                return None
            return film
            # Если фильма нет в кеше, то ищем его в Elasticsearch
        film = await self._get_film_from_elastic(film_id, model)
        if not film:
            # Если он отсутствует в Elasticsearch, значит, фильма вообще нет в базе
            return None

        return film

    async def get_films_search(
            self,
            query: str,
            page: int,
            size: int,
    ) -> list[FilmBase]:
        films = await self._get_films_search_from_elastic(query, page, size)
        if not films:
            return []
        return films

    async def _get_film_from_elastic(self, film_id: str, model: FilmBase | Film) -> Optional[Film]:
        try:
            doc = await self.elastic.get('movies', film_id)
        except NotFoundError:
            return None
        return model(**doc['_source'])

    async def _get_films_from_elastic(self,
                                      sort,
                                      size,
                                      page,
                                      filter_genre) -> list[FilmBase]:
        query_body = {
            "query": {
            }
        }
        if not filter_genre:
            query_body['query']["match_all"] = {}
        if sort:
            query_body['sort'] = {
                "imdb_rating": {
                    "order": "desc"
                }
            }
        if size:
            query_body['size'] = size
        if page:
            query_body['from'] = page
        if filter_genre:
            query_body['query'] = {
                "nested": {
                    "path": "genre",
                    "query": {
                        "bool": {
                            "should": [
                                {
                                    "match": {"genre.uuid": filter_genre}
                                }
                            ]
                        }
                    }

                }
            }
        try:
            doc = await self.elastic.search(
                index='movies',
                body=query_body)
        except NotFoundError:
            return []
        if doc['hits']['total']['value'] > 0:
            return [FilmBase(**movie['_source']) for movie in doc['hits']['hits']]
        return []

    async def _get_films_search_from_elastic(
            self,
            query: str,
            page: int,
            size: int,
    ):
        query_body = {}

        if not query:
            return None

        if page:
            query_body['from'] = page

        if size:
            query_body["size"] = size

        query_body["query"] = {
            "match": {
                "title": {
                    "query": query,
                    "fuzziness": "AUTO"
                }
            }
        }
        try:
            doc = await self.elastic.search(body=query_body, index='movies')
        except NotFoundError:
            return []
        return [FilmBase(**movie['_source']) for movie in doc['hits']['hits']]


@lru_cache()
def get_film_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmService:
    return FilmService(redis, elastic)
