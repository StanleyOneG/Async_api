from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request

from cache.redis_cache import cache
from services.genre import GenreService, get_genre_service
from .schemas import Genre

router = APIRouter()


@router.get(
    '/',
    summary="Жанры",
    description="Жанры",
    response_description="Список жанров",
    tags=["Жанры"],
    response_model=list[Genre],
)
@cache
async def genre_list(
    request: Request,
    genre_service: GenreService = Depends(get_genre_service),
):
    elastic_index = genre_service.elastic_index
    genres = await genre_service.get_list()
    if not genres:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='genres not found',
        )
    return [Genre(uuid=genre.uuid, name=genre.name) for genre in genres]


@router.get(
    '/{genre_id}',
    summary="Жанр",
    description="Жанр по ID",
    response_description="Жанр по ID",
    tags=["Жанры"],
    response_model=Genre,
)
@cache
async def genre_details(
    request: Request,
    genre_id: UUID,
    genre_service: GenreService = Depends(get_genre_service),
) -> Genre:
    model = genre_service.model
    genre = await genre_service.get_by_id(genre_id, model)
    if not genre:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='genre not found',
        )

    return Genre(uuid=genre.uuid, name=genre.name)
