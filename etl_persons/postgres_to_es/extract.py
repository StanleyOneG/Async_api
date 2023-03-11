"""Module for checking update status and extracting persons data."""

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
        'person',
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
        Check if tables have been updated and save persons ids to Redis.

        Args:
            last_checked: datetime - last check on the database updates.

        Returns:
            Set of movies ids that need to be updated at the moment.
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
            persons = [item for item in updates_in_tables['person'].keys()]

            if persons:
                pg_cursor.execute(
                    """
                    SELECT id FROM person WHERE person.id IN {0}
                    """.format(
                        re.sub(
                            r',\s*\)',
                            ')',
                            str(tuple(persons)),
                        ),
                    ),
                )

            persons_update = [
                person[0] for person in pg_cursor.fetchall()
            ]

        persons_need_to_update = set().union(
            persons_update,
        )
        self.redis.set(
            'person_last_checked',
            json.dumps(
                datetime.now(timezone.utc),
                default=str,
            ),
        )

        if persons_need_to_update:
            for person in persons_need_to_update:
                self.redis.sadd('persons_need_to_update', person)
            logger.info(
                'There are %d persons need to be updated',
                len(persons_need_to_update),
            )
            return persons_need_to_update

        logger.info('There are no persons for update')
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
    def extract_person_data(
        self,
        persons: list,
    ) -> Generator:
        """
        Extract whole movies information from the PostgreSQL database.

        Args:
            movies: list of movies ids to extract from the PostgreSQL database.

        Yields:
            Dictionary mapping movies information.
        """
        with self.pg_connection.cursor() as pg_cursor:
            for person in persons:
                pg_cursor.execute(
                    """
                    SELECT 
                        p.id, 
                        p.full_name, 
                        COALESCE(CONCAT_WS(',', ARRAY_AGG(pfw.film_work_id)), '') AS film_work_ids
                    FROM person p
                    LEFT JOIN person_film_work pfw ON p.id = pfw.person_id
                    WHERE p.id = '{0}'
                    GROUP BY p.id, p.full_name
                    """.format(
                        person,
                    ),
                )
                person_data = dict(pg_cursor.fetchall()[0])
                yield person_data
