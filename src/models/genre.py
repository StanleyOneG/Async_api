from uuid import UUID

import orjson
from pydantic import BaseModel


def orjson_dumps(v, *, default):
    return orjson.dumps(v, default=default).decode()


class Genre(BaseModel):
    name: str
    uuid: UUID

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps
