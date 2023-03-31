from typing import List, Union
from uuid import UUID

from pydantic import BaseModel
from models.simple_model import SimpleModel

from .genre import Genre
from .person import PersonBase


class FilmBase(BaseModel):
    uuid: UUID
    title: str
    imdb_rating: float | None


class Film(SimpleModel, FilmBase):
    description: str | None
    genre: Union[List[Genre], None]
    actors: Union[List[PersonBase], None]
    writers: Union[List[PersonBase], None]
    directors: Union[List[PersonBase], None]
