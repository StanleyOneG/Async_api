from typing import Any
from uuid import UUID

import orjson
from pydantic import BaseModel


def orjson_dumps(v, *, default):
    return orjson.dumps(v, default=default).decode()


class PersonBase(BaseModel):
    uuid: UUID | Any
    full_name: str


class PersonWithFilms(PersonBase):
    film_work_ids: list[str | None]

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps
