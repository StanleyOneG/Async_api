"""Module for transforming movies data to relevant format for Elasticsearch."""


import uuid
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Generator

from redis import Redis


@dataclass
class Filmwork:
    """Class for movie data validation."""

    title: str
    description: str | None
    rating: float | None
    file_path: str | None
    type: str
    creation_date: datetime | None
    updated_at: datetime
    genres: list[dict]
    persons: list[dict]
    filmwork_id: uuid.UUID


@dataclass
class Transformer:
    """Transformer class for movie data to index it in Elasticsearch."""

    redis: Redis

    def get_transformed_movies(
        self,
        movies_data: Generator,
    ) -> Generator:
        """
        Prepare movies data for convenient transformation.

        Args:
            movies_data: generator - movie data dictionary.

        Yields:
            Validated dictionary mapping movies data.
        """
        for row in movies_data:
            film = asdict(Filmwork(**row))
            yield film

    def prepare_for_es(
        self,
        movies_data: Generator,
    ) -> Generator:
        """
        Traform movies data for indexing them in Elasticsearch.

        Args:
            movies_data: generator - validated movie data dict

        Yields:
            Dictionary mapping movies data for in Elasticsearch.
        """
        movie = {}
        for film in self.get_transformed_movies(movies_data):
            movie['id'] = film['filmwork_id']
            movie['imdb_rating'] = film['rating']
            movie['genre'] = [genre['genre_name'] for genre in film['genres']]
            movie['title'] = film['title']
            movie['description'] = film['description']
            movie['director'] = [
                person['person_name']
                for person in film['persons']
                if person['person_role'] == 'director'
            ]

            movie['actors_names'] = [
                person['person_name']
                for person in film['persons']
                if person['person_role'] == 'actor'
            ]
            movie['writers_names'] = [
                person['person_name']
                for person in film['persons']
                if person['person_role'] == 'writer'
            ]
            movie['actors'] = [
                {
                    key.split('_')[1]: value
                    for (key, value) in person.items()
                    if key in ['person_id', 'person_name']
                }
                for person in film['persons']
                if person['person_role'] == 'actor'
            ]
            movie['writers'] = [
                {
                    key.split('_')[1]: value
                    for (key, value) in person.items()
                    if key in ['person_id', 'person_name']
                }
                for person in film['persons']
                if person['person_role'] == 'writer'
            ]

            yield {
                '_index': 'movies',
                '_id': movie['id'],
                '_source': movie,
            }
