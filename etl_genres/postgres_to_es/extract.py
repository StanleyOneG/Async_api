"""Module for checking update status and extracting genres data."""

import json
import logging
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Generator

import backoff
from psycopg2.errors import (
    ConnectionDoesNotExist,
    ConnectionException,
    ConnectionFailure,
    InterfaceError,
    OperationalError,
)
from psycopg2.extensions import connection
from redis import Redis

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ExtractorFromPostgres:
    """Class for checking movies updates and extraction from postgres."""

    pg_connection: connection
    redis: Redis

    tables = [
        'genre',
    ]

    @backoff.on_exception(
        backoff.expo,
        (
            OperationalError,
            InterfaceError,
            ConnectionDoesNotExist,
            ConnectionFailure,
            ConnectionException,
        ),
    )
    def find_tables_updates(self, last_checked: datetime) -> set | None:
        """
        Check if tables have been updated and save genres ids to Redis.

        Args:
            last_checked: datetime - last check on the database updates.

        Returns:
            Set of movies ids that need to be updated in the moment.
            None if tables have not been updated.
        """
        with self.pg_connection.cursor() as pg_cursor:
            updates_in_tables = {}
            logger.info('Checking tables for updates')
            for table in self.tables:
                pg_cursor.execute(
                    f"""
                    SELECT id, updated_at FROM {table}
                    WHERE updated_at > TIMESTAMP '{last_checked}'
                    ORDER BY updated_at
                    """,
                )
                updates_in_tables[table] = dict(pg_cursor.fetchall())
            genres = [item for item in updates_in_tables['genre'].keys()]

            if genres:
                pg_cursor.execute(
                    """
                    SELECT id FROM genre WHERE genre.id IN {0}
                    """.format(
                        re.sub(
                            r',\s*\)',
                            ')',
                            str(tuple(genres)),
                        ),
                    ),
                )

            genres_update = [
                genre[0] for genre in pg_cursor.fetchall()
            ]

        genres_need_to_update = set().union(
            genres_update,
        )
        self.redis.set(
            'genre_last_checked',
            json.dumps(
                datetime.now(timezone.utc),
                default=str,
            ),
        )

        if genres_need_to_update:
            for genre in genres_need_to_update:
                self.redis.sadd('genres_need_to_update', genre)
            logger.info(
                'There are %d genres need to be updated',
                len(genres_need_to_update),
            )
            return genres_need_to_update

        logger.info('There are no genres for update')
        return None

    @backoff.on_exception(
        backoff.expo,
        (
            OperationalError,
            InterfaceError,
            ConnectionDoesNotExist,
            ConnectionFailure,
            ConnectionException,
        ),
    )
    def extract_genre_data(
        self,
        genres: list,
    ) -> Generator:
        """
        Extract whole movies information from the PostgreSQL database.

        Args:
            movies: list of movies ids to extract from the PostgreSQL database.

        Yields:
            Dictionary mapping movies information.
        """
        with self.pg_connection.cursor() as pg_cursor:
            for genre in genres:
                pg_cursor.execute(
                    """
                    SELECT
                        genre.id,
                        genre.name,
                        genre.description
                    FROM genre
                    WHERE genre.id = '{0}'
                    """.format(
                        genre,
                    ),
                )
                genre_data = dict(pg_cursor.fetchall()[0])
                yield genre_data
