import asyncio
from http import HTTPStatus
from typing import List, Union

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response

from cache.redis_cache import cache
from services.film import FilmService, get_film_service
from .schemas import Film, FilmBase

router = APIRouter()


@router.get(
    '/{film_id}/similar',
    summary="Похожие фильмы",
    description="Список похожих фильмов по жанру",
    response_description="Похожие фильму по жанру",
    tags=["Похожие фильмы"],
    response_model=List[FilmBase],
)
@cache
async def similar_films(
    request: Request,
    film_id: str,
    film_service: FilmService = Depends(get_film_service),
) -> list[FilmBase]:
    film = await film_service.get_by_id(film_id, Film)
    if not film:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='film not found',
        )
    genre_ids = [genre.uuid for genre in film.genre]
    result = await asyncio.gather(
        *[
            film_service.get_films(
                sort='imdb_rating', size=10, page=0, filter_genre=genre_id
            )
            for genre_id in genre_ids
        ],
    )
    similars = []
    for group in result:
        for film in group:
            if film.uuid not in similars:
                similars.append(film)
    return sorted(similars, key=lambda film: film.imdb_rating, reverse=True)


@router.get(
    '/search',
    summary="Поиск кинопроизведений",
    description="Полнотекстовый поиск по кинопроизведениям",
    response_description="Название и рейтинг фильма",
    tags=["Полнотекстовый поиск"],
    response_model=List[FilmBase],
)
@cache
async def search_films(
    request: Request,
    query: str = Query(default=None),
    page: int = Query(default=0, alias='page_number', ge=0),
    size: int = Query(default=50, alias='page_size', ge=1, le=1000),
    film_service: FilmService = Depends(get_film_service),
) -> List[FilmBase]:
    films = await film_service.get_films_search(query, page, size)
    return films


@router.get(
    "/",
    summary="Кинопроизведения",
    description="Кинопроизведения",
    response_description="Список кинопроизведений",
    tags=["Кинопроизведения"],
    response_model=List[FilmBase],
)
@cache
async def films(
    request: Request,
    sort: Union[str, None] = Query(
        default='imdb_rating', alias='-imdb_rating'
    ),
    page: int = Query(default=0, alias='page_number', ge=0),
    size: int = Query(default=50, alias='page_size', ge=1, le=1000),
    filter_genre: str = Query(default=None, alias='genre'),
    film_service: FilmService = Depends(get_film_service),
) -> List[FilmBase]:
    films = await film_service.get_films(
        page,
        size,
        sort,
        filter_genre,
    )
    return films


@router.get(
    '/{film_id}',
    summary="Кинопроизведение",
    description="Кинопроизведение по ID",
    response_description="Детали кинопроизведения по ID",
    tags=["Кинопроизведение"],
    response_model=Film,
)
@cache
async def film_details(
    request: Request,
    film_id: str,
    film_service: FilmService = Depends(get_film_service),
) -> Film:
    film = await film_service.get_by_id(film_id, Film)
    if not film:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='film not found'
        )

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
