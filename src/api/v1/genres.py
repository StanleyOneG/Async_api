from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request

from api.v1.schemas import GenreSchema
from api.v1.utils import PaginateQueryParams
from cache.redis_cache import cache
from services.base_service import MovieService
from services.storage_service import get_genres_service
from auth.jwt import check_auth

router = APIRouter()


@router.get(
    '/',
    summary="Жанры",
    description="Жанры",
    response_description="Список жанров",
    tags=["Жанры"],
    response_model=list[GenreSchema],
)
@check_auth(endpoint_permission='subscriber')
@cache
async def genre_list(
    request: Request,
    parameters: PaginateQueryParams = Depends(),
    genre_service: MovieService = Depends(get_genres_service),
):
    genres = await genre_service.search_data(parameters=parameters)
    if not genres:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='genres not found',
        )
    return [GenreSchema(**genre) for genre in genres]


@router.get(
    '/{genre_id}',
    summary="Жанр",
    description="Жанр по ID",
    response_description="Жанр по ID",
    tags=["Жанры"],
    response_model=GenreSchema,
)
@check_auth(endpoint_permission='subscriber')
@cache
async def genre_details(
    request: Request,
    genre_id: UUID,
    genre_service: MovieService = Depends(get_genres_service),
) -> GenreSchema:
    genre = await genre_service.get_by_id(id=genre_id)
    if not genre:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='genre not found',
        )

    return GenreSchema(**genre)
