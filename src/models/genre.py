from uuid import UUID

from models.simple_model import SimpleModel


class Genre(SimpleModel):
    name: str
    uuid: UUID
