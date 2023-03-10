"""Module for loading persons data to Elasticsearch index."""


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
    index = 'persons'


@dataclass
class ElasticLoader:
    """Class for loading persons data to Elasticsearch index."""

    elastic: Elasticsearch
    redis: Redis
    index_info: FilePath
    chunk_size: int

    @backoff.on_exception(backoff.expo, (ConnectionError, TransportError))
    def create_index(self) -> None:
        """Create Elasticsearch index if it does not exist."""
        with open(self.index_info, 'r') as file:
            data = json.load(
                file,
            )

        index = ElasticIndex.parse_raw(str(data).replace("'", '"'))

        try:
            self.elastic.indices.create(
                index='persons',
                settings=index.settings,
                mappings=index.mappings,
            )
        except TransportError as transport_error:
            logger.error(transport_error)

    @backoff.on_exception(backoff.expo, (ConnectionError, TransportError))
    def load_data(self, persons_data: Generator) -> None:
        """
        Load persons data to Elasticsearch index by chunk.

        Args:
            persons_data: generator - dict of validated data.

        """
        if not self.elastic.indices.exists(index=['persons']):
            self.create_index()
            logger.info('Index created')

            try:
                helpers.bulk(
                    self.elastic,
                    persons_data,
                    chunk_size=self.chunk_size,
                )
                logger.info('Loaded data to Elasticsearch')

            except Exception as load_error:
                logger.error(load_error)
