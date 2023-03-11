import orjson
from typing import List, Union

# Используем pydantic для упрощения работы при перегонке данных из json в объекты
from pydantic import BaseModel

from .genre import Genre
from .person import PersonBase


def orjson_dumps(v, *, default):
    # orjson.dumps возвращает bytes, а pydantic требует unicode, поэтому декодируем
    return orjson.dumps(v, default=default).decode()


class FilmBase(BaseModel):
    uuid: str
    title: str
    imdb_rating: float | None


class Film(FilmBase):
    description: str | None
    genre: Union[List[Genre], None]
    actors: Union[List[PersonBase], None]
    writers: Union[List[PersonBase], None]
    directors: Union[List[PersonBase], None]

    class Config:
        # Заменяем стандартную работу с json на более быструю
        json_loads = orjson.loads
        json_dumps = orjson_dumps
