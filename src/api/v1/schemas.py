from typing import List, Union
from uuid import UUID

from pydantic import BaseModel

from models.genre import Genre
from models.person import PersonBase


class ObjectModel(BaseModel):
    uuid: UUID


class FilmBase(ObjectModel):
    title: str
    imdb_rating: float


class Film(FilmBase):
    description: str | None
    genre: Union[List[Genre], Genre, None]
    actors: Union[List[PersonBase], PersonBase, None]
    writers: Union[List[PersonBase], PersonBase, None]
    directors: Union[List[PersonBase], PersonBase, None]


class Genre(ObjectModel):
    name: str


class Person(ObjectModel):
    full_name: str
    films: list
