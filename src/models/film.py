import orjson
from typing import List, Union

# Используем pydantic для упрощения работы при перегонке данных из json в объекты
from pydantic import BaseModel

def orjson_dumps(v, *, default):
    # orjson.dumps возвращает bytes, а pydantic требует unicode, поэтому декодируем
    return orjson.dumps(v, default=default).decode()

class Film(BaseModel):
    id: str
    title: str
    description: str
    imdb_rating: float
    # genre: Union[List[str], str, None]
    # actors: Union[List[str], str, None]
    # writers: Union[List[str], str, None]
    # directors: Union[List[str], str, None]

    class Config:
        # Заменяем стандартную работу с json на более быструю
        json_loads = orjson.loads
        json_dumps = orjson_dumps