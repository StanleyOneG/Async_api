"""Module for base model class."""

import orjson
from pydantic import BaseModel


def orjson_dumps(v, *, default):
    """Change the default json to faster one."""
    return orjson.dumps(v, default=default).decode()


class SimpleModel(BaseModel):
    """Base model class."""

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps
