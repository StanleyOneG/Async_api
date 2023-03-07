"""Module for loading movies data to Elasticsearch index."""


import json
import logging
from dataclasses import dataclass
from typing import Generator

import backoff
from elasticsearch import Elasticsearch, helpers
from elasticsearch.exceptions import ConnectionError, TransportError
from pydantic import BaseModel, FilePath
from redis import Redis

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ElasticIndex(BaseModel):
    """Class for elasticsearch index settings validation."""

    settings: dict
    mappings: dict
    index_movies = 'movies'
    index_genres = 'genres'


@dataclass
class ElasticLoader:
    """Class for loading movies data to Elasticsearch index."""

    elastic: Elasticsearch
    redis: Redis
    index_movies_info: FilePath
    index_genres_info: FilePath
    chunk_size: int

    @backoff.on_exception(backoff.expo, (ConnectionError, TransportError))
    def create_movies_index(self) -> None:
        """Create Elasticsearch index if it does not exist."""
        with open(self.index_movies_info, 'r') as file:
            data = json.load(
                file,
            )

        index_movies = ElasticIndex.parse_raw(str(data).replace("'", '"'))

        try:
            self.elastic.indices.create(
                index='movies',
                settings=index_movies.settings,
                mappings=index_movies.mappings,
            )
        except TransportError as transport_error:
            logger.error(transport_error)

    @backoff.on_exception(backoff.expo, (ConnectionError, TransportError))
    def create_genres_index(self) -> None:
        """Create Elasticsearch index if it does not exist."""
        with open(self.index_genres_info, 'r') as file:
            data = json.load(
                file,
            )

        index_genres = ElasticIndex.parse_raw(str(data).replace("'", '"'))

        try:
            self.elastic.indices.create(
                index='genres',
                settings=index_genres.settings,
                mappings=index_genres.mappings,
            )
        except TransportError as transport_error:
            logger.error(transport_error)

    @backoff.on_exception(backoff.expo, (ConnectionError, TransportError))
    def load_movies_data(self, movies_data: Generator) -> None:
        """
        Load movies data to Elasticsearch index by chunk.

        Args:
            movies_data: generator - dict of validated data.

        """
        if not self.elastic.indices.exists(index=['movies']):
            self.create_movies_index()
            logger.info('Index "movies" created')

            try:
                helpers.bulk(
                    self.elastic,
                    movies_data,
                    chunk_size=self.chunk_size,
                )
                logger.info('Loaded data to Elasticsearch/_movies')

            except Exception as load_error:
                logger.error(load_error)

    @backoff.on_exception(backoff.expo, (ConnectionError, TransportError))
    def load_genres_data(self, genres_data: Generator) -> None:
        """
        Load genres data to Elasticsearch index by chunk.

        Args:
            genres_data: generator - dict of validated data.

        """
        if not self.elastic.indices.exists(index=['genres']):
            self.create_genres_index()
            logger.info('Index "genres" created')

            try:
                helpers.bulk(
                    self.elastic,
                    genres_data,
                    chunk_size=self.chunk_size,
                )
                logger.info('Loaded data to Elasticsearch/_genres')

            except Exception as load_error:
                logger.error(load_error)
