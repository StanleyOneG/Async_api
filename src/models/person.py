from typing import Any
from uuid import UUID

from pydantic import BaseModel
from models.simple_model import SimpleModel


class PersonBase(BaseModel):
    uuid: UUID | Any
    full_name: str


class PersonWithFilms(SimpleModel, PersonBase):
    film_work_ids: list[str | None]
