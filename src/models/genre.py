import orjson
from typing import List, Union

from pydantic import BaseModel


def orjson_dumps(v, *, default):
    return orjson.dumps(v, default=default).decode()


class Genre(BaseModel):
    name: str
    uuid: str

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps
