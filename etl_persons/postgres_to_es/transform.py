"""Module for transforming persons data to relevant format for Elasticsearch."""


import uuid
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Generator
import logging

from redis import Redis

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class Person:
    """Class for person data validation."""

    full_name: str
    id: uuid.UUID


@dataclass
class Transformer:
    """Transformer class for person data to index in Elasticsearch."""

    redis: Redis

    def get_transformed_persons(
        self,
        persons_data: Generator,
    ) -> Generator:
        """
        Prepare persons data for convenient transformation.

        Args:
            movies_data: generator - persons data dictionary.

        Yields:
            Validated dictionary mapping persons data.
        """
        for row in persons_data:
            person = asdict(Person(**row))
            yield person

    def prepare_for_es(
        self,
        persons_data: Generator,
    ) -> Generator:
        """
        Traform persons data for indexing them in Elasticsearch.

        Args:
            persons_data: generator - validated persons data dict

        Yields:
            Dictionary mapping persons data for in Elasticsearch.
        """
        person = {}
        for data in self.get_transformed_persons(persons_data):
            person['uuid'] = data['id']
            person['full_name'] = data['full_name']
            yield {
                '_index': 'persons',
                '_id': person['uuid'],
                '_source': person,
            }
