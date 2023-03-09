from http import HTTPStatus
from typing import List
from fastapi import HTTPException
from fastapi import APIRouter
from pydantic import BaseModel

from models.genre import Genre
from services.genre import GenreService, get_genre_service
from fastapi import Depends, Request


router = APIRouter()


class Genre(BaseModel):

    uuid: str
    name: str


@router.get('/', response_model=list[Genre])
async def genre_list(
    request: Request, genre_service: GenreService = Depends(get_genre_service)
):
    genres = await genre_service.get_genres_list(request)
    # if not genres:
    #     raise HTTPException(
    #         status_code=HTTPStatus.NOT_FOUND,
    #         detail='genres not found',
    #     )
    # return genres
    return [Genre(uuid=genre.uuid, name=genre.name) for genre in genres]


@router.get('/{genre_id}', response_model=Genre)
async def genre_details(
    genre_id: str, genre_service: GenreService = Depends(get_genre_service)
) -> Genre:
    genre = await genre_service.get_by_id(genre_id)
    if not genre:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='genre not found',
        )

    return Genre(uuid=genre.uuid, name=genre.name)
