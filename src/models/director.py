from uuid import UUID
from models.simple_model import SimpleModel


class Director(SimpleModel):
    id: UUID
    name: str
