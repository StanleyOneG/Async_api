from http import HTTPStatus
from fastapi import HTTPException
from fastapi import APIRouter
from pydantic import BaseModel

from models.genre_model import GenreModel
from services.genre import GenreService, get_genre_service
from fastapi import Depends


router = APIRouter()


class Genre(BaseModel):

    id: str
    name: str
    description: str


@router.get('/{genre_id}', response_model=GenreModel)
async def genre_details(
    genre_id: str, genre_service: GenreService = Depends(get_genre_service)
) -> GenreModel:
    genre = await genre_service.get_by_id(genre_id)
    if not genre:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='genre not found'
        )

    return GenreModel(
        id=genre.id, name=genre.name, description=genre.description
    )
