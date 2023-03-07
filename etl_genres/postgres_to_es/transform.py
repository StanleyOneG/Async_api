"""Module for transforming genres data to relevant format for Elasticsearch."""


import uuid
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Generator
import logging

from redis import Redis

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class Genre:
    """Class for genre data validation."""

    name: str
    id: uuid.UUID
    description: str | None


@dataclass
class Transformer:
    """Transformer class for genre data to index in Elasticsearch."""

    redis: Redis

    def get_transformed_genres(
        self,
        genres_data: Generator,
    ) -> Generator:
        """
        Prepare genres data for convenient transformation.

        Args:
            movies_data: generator - genre data dictionary.

        Yields:
            Validated dictionary mapping genres data.
        """
        for row in genres_data:
            genre = asdict(Genre(**row))
            yield genre

    def prepare_for_es(
        self,
        genres_data: Generator,
    ) -> Generator:
        """
        Traform genres data for indexing them in Elasticsearch.

        Args:
            genres_data: generator - validated genre data dict

        Yields:
            Dictionary mapping genres data for in Elasticsearch.
        """
        genre = {}
        for data in self.get_transformed_genres(genres_data):
            genre['id'] = data['id']
            genre['name'] = data['name']
            genre['description'] = data['description']
            yield {
                '_index': 'genres',
                '_id': genre['id'],
                '_source': genre,
            }
