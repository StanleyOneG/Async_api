import orjson
from typing import List, Union

<<<<<<< HEAD
# Используем pydantic для упрощения работы при перегонке данных из json в объекты
from pydantic import BaseModel

def orjson_dumps(v, *, default):
    # orjson.dumps возвращает bytes, а pydantic требует unicode, поэтому декодируем
    return orjson.dumps(v, default=default).decode()

class Genre(BaseModel):
    id: str
    name: str

    class Config:
        # Заменяем стандартную работу с json на более быструю
        json_loads = orjson.loads
        json_dumps = orjson_dumps
=======
from pydantic import BaseModel

def orjson_dumps(v, *, default):
    return orjson.dumps(v, default=default).decode()

class Genre(BaseModel):
    name: str
    uuid: str

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps
>>>>>>> main
