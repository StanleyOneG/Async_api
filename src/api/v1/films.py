import asyncio
from http import HTTPStatus
from typing import Any, Union, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from services.film import FilmService, get_film_service

from models.genre import Genre
from models.person import PersonBase

router = APIRouter()


class FilmBase(BaseModel):
    uuid: str
    title: str
    imdb_rating: float


class Film(FilmBase):
    description: str | None
    genre: Union[List[Genre], None]
    actors: Union[List[PersonBase], None]
    writers: Union[List[PersonBase], None]
    directors: Union[List[PersonBase], None]

@router.get('/{film_id}/similar', description='Similar films defined by genre')
async def similar_films(film_id: str, film_service: FilmService = Depends(get_film_service)) -> list[FilmBase]:
    film = await film_service.get_by_id(film_id, Film)
    if not film:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='film not found'
        )
    genre_ids = [genre.uuid for genre in film.genre]
    result = await asyncio.gather(
        *[film_service.get_films(sort='imdb_rating', 
                                 size=10, page=0, 
                                 filter_genre=genre_id) 
          for genre_id in genre_ids],
    )
    return result

@router.get('/search')
async def search_films(
    query: str = Query(default=None),
    page: int = Query(default=0, alias='page_number', ge=0),
    size: int = Query(default=50, alias='page_size', ge=1, le=1000),
    film_service: FilmService = Depends(get_film_service),
) -> List[FilmBase]:
    films = await film_service.get_films_search(query, page, size)
    return films

@router.get("/")
async def films(
    sort: Union[str, None] = Query(
        default='imdb_rating', alias='-imdb_rating'
    ),
    size: int = Query(default=50, alias='page_size', ge=0),
    page: int = Query(default=0, alias='page_number', ge=0),
    filter_genre: str = Query(default=None, alias='genre'),
    film_service: FilmService = Depends(get_film_service),
) -> List[FilmBase]:
    films = await film_service.get_films(sort, size, page, filter_genre)
    return films


# Внедряем FilmService с помощью Depends(get_film_service)
@router.get('/{film_id}', response_model=Film)
async def film_details(
    film_id: str, film_service: FilmService = Depends(get_film_service)
) -> Film:
    film = await film_service.get_by_id(film_id, Film)
    if not film:
        # Если фильм не найден, отдаём 404 статус
        # Желательно пользоваться уже определёнными HTTP-статусами, которые содержат enum
        # Такой код будет более поддерживаемым
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='film not found'
        )

    # Перекладываем данные из models.Film в Film
    # Обратите внимание, что у модели бизнес-логики есть поле description
    # Которое отсутствует в модели ответа API.
    # Если бы использовалась общая модель для бизнес-логики и формирования ответов API
    # вы бы предоставляли клиентам данные, которые им не нужны
    # и, возможно, данные, которые опасно возвращать

    return Film(
        uuid=film.uuid,
        title=film.title,
        description=film.description,
        imdb_rating=film.imdb_rating,
        actors=film.actors,
        writers=film.writers,
        directors=film.directors,
        genre=film.genre,
    )

