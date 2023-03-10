from http import HTTPStatus
from typing import Union, List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from services.genre import GenreService, get_genre_service

from models.genre import Genre

router = APIRouter()


class Genre(BaseModel):
    uuid: str
    name: str


@router.get('/{genre_id}', response_model=Genre)
async def film_details(genre_id: str, genre_service: GenreService = Depends(get_genre_service)) -> Genre:
    genre = await genre_service.get_by_id(genre_id)
    if not genre:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='genre not found')

    return Genre(
        uuid=genre.uuid,
        name=genre.name)