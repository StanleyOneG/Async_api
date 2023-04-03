import asyncio
from http import HTTPStatus
from typing import List, Union
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response

from cache.redis_cache import cache
from api.v1.schemas import Film, FilmBase
from api.v1.utils import PaginateQueryParams
from services.storage_service import get_storage_service
from services.base_service import MovieService

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
    film_id: UUID,
    parameters: PaginateQueryParams = Depends(),
    movie_service: MovieService = Depends(get_storage_service),
) -> list[FilmBase]:
    data_from_storage = await movie_service.get_by_id(film_id)
    film = Film(**data_from_storage)
    if not film:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='film not found',
        )
    genre_ids = [genre.uuid for genre in film.genre]
    list_data_from_storage = await asyncio.gather(
        *[
            movie_service.search_data(
                sort='imdb_rating',
                parameters=parameters,
                filter=genre_id,
            )
            for genre_id in genre_ids
        ],
    )
    similars = []
    for group in list_data_from_storage:
        group_of_films = [FilmBase(**film) for film in group]
        for film in group_of_films:
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
    paginate_query_params: PaginateQueryParams = Depends(),
    movie_service: MovieService = Depends(get_storage_service),
) -> List[FilmBase]:
    films = await movie_service.search_data(query, paginate_query_params)
    if not films:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='films not found'
        )
    return [FilmBase(**film) for film in films]


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
    parameters: PaginateQueryParams = Depends(),
    filter_genre: UUID = Query(default=None, alias='genre'),
    movie_service: MovieService = Depends(get_storage_service),
) -> List[FilmBase]:
    films = await movie_service.search_data(
        parameters=parameters,
        sort=sort,
        filter=filter_genre,
    )
    return [FilmBase(**film) for film in films]


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
    film_id: UUID,
    movie_service: MovieService = Depends(get_storage_service),
) -> Film:
    film = await movie_service.get_by_id(id=film_id)
    if not film:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='film not found'
        )
    return Film(**film)

    # return Film(
    #     uuid=film.get('uuid'),
    #     title=film.get('title'),
    #     description=film.get('description'),
    #     imdb_rating=film.get('imdb_rating'),
    #     actors=film.get('actors'),
    #     writers=film.get('writers'),
    #     directors=film.get('directors'),
    #     genre=film.get('genre'),
    # )
