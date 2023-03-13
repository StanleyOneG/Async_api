from functools import lru_cache
import json
from typing import Optional

from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends, HTTPException
from redis.asyncio import Redis

from db.elastic import get_elastic
from db.redis import get_redis
from models.film import Film, FilmBase

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут


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
    async def get_by_id(self, film_id: str) -> Optional[Film]:
        # Пытаемся получить данные из кеша, потому что оно работает быстрее
        film = await self._film_from_cache(film_id)
        if not film:
            # Если фильма нет в кеше, то ищем его в Elasticsearch
            film = await self._get_film_from_elastic(film_id)
            if not film:
                # Если он отсутствует в Elasticsearch, значит, фильма вообще нет в базе
                return None
            # Сохраняем фильм  в кеш
            await self._put_film_to_cache(film)

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

    async def _get_film_from_elastic(self, film_id: str) -> Optional[Film]:
        try:
            doc = await self.elastic.get('movies', film_id)
        except NotFoundError:
            return None
        return Film(**doc['_source'])

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

    async def _film_from_cache(self, film_id: str) -> Optional[Film]:
        # Пытаемся получить данные о фильме из кеша, используя команду get
        # https://redis.io/commands/get/
        data = await self.redis.get(film_id)
        if not data:
            return None

        # pydantic предоставляет удобное API для создания объекта моделей из json
        film = Film.parse_raw(data)
        return film
    
    async def _put_film_to_cache(self, film: Film):
        # Сохраняем данные о фильме, используя команду set
        # Выставляем время жизни кеша — 5 минут
        # https://redis.io/commands/set/
        # pydantic позволяет сериализовать модель в json
        await self.redis.set(film.uuid, film.json(), FILM_CACHE_EXPIRE_IN_SECONDS)

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
            
        query_body["query"]= {
            "match": {
                "title": {
                    "query": query,
                    "fuzziness": "AUTO"
                }
            }
        }
        try:
            doc = await self.elastic.search(body = query_body, index='movies')
        except NotFoundError:
            return []
        return [FilmBase(**movie['_source']) for movie in doc['hits']['hits']]

@lru_cache()
def get_film_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmService:
    return FilmService(redis, elastic)
