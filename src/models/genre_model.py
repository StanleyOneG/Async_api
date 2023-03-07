from pydantic import BaseModel

from models_mixins import OrjsonMixin


class GenreModel(OrjsonMixin, BaseModel):
    """Model for Genres"""

    id: str
    name: str
    description: str
