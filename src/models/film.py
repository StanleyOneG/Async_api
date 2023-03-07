import orjson
from typing import List, Union

# Используем pydantic для упрощения работы при перегонке данных из json в объекты
from pydantic import BaseModel

from .genre import Genre
from .director import Director

def orjson_dumps(v, *, default):
    # orjson.dumps возвращает bytes, а pydantic требует unicode, поэтому декодируем
    return orjson.dumps(v, default=default).decode()

class Film(BaseModel):
    id: str
    title: str
    description: str
    imdb_rating: float
    # genre: Union[List[Genre], None]
    # actors: Union[List[str], None]
    # writers: Union[List[str], None]
    directors: Union[List[Director], None]

    class Config:
        # Заменяем стандартную работу с json на более быструю
        json_loads = orjson.loads
        json_dumps = orjson_dumps