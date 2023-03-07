"""Module for checking update status and extracting movies data."""

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
        'film_work',
        'genre',
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
        Check if tables have been updated and save movies ids to Redis.

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
            movies = [item for item in updates_in_tables['film_work'].keys()]
            persons = [item for item in updates_in_tables['person'].keys()]
            genres = [item for item in updates_in_tables['genre'].keys()]

            if persons:
                pg_cursor.execute(
                    """
                    SELECT DISTINCT
                        filmwork.id
                    FROM film_work AS filmwork
                    LEFT JOIN
                        person_film_work as person_film_work 
                            ON
                        filmwork.id = person_film_work.film_work_id
                    LEFT JOIN 
                        person as person 
                            ON 
                        person.id = person_film_work.person_id
                    WHERE person.id IN {0}
                    """.format(
                        re.sub(
                            r',\s*\)',
                            ')',
                            str(tuple(persons)),
                        ),
                    ),
                )
            movies_from_persons_update = [
                movie[0] for movie in pg_cursor.fetchall()
            ]

            if genres:
                pg_cursor.execute(
                    """
                    SELECT DISTINCT
                        filmwork.id
                    FROM film_work AS filmwork
                    LEFT JOIN 
                        genre_film_work as genre_film_work 
                            ON 
                        filmwork.id = genre_film_work.film_work_id
                    LEFT JOIN 
                        genre as genre 
                            ON 
                        genre.id = genre_film_work.genre_id
                    WHERE genre.id IN {0}
                    """.format(
                        re.sub(
                            r',\s*\)',
                            ')',
                            str(tuple(genres)),
                        ),
                    ),
                )

            movies_form_genres_update = [
                movie[0] for movie in pg_cursor.fetchall()
            ]

        movies_need_to_update = set().union(
            movies,
            movies_form_genres_update,
            movies_from_persons_update,
        )
        self.redis.set(
            'last_checked',
            json.dumps(
                datetime.now(timezone.utc),
                default=str,
            ),
        )

        if movies_need_to_update:
            for movie in list(movies_need_to_update):
                self.redis.sadd('need_to_update', movie)
            logger.info(
                'There are %d movies need to be updated',
                len(movies_need_to_update),
            )
        if genres is not None:
            for genre in genres:
                self.redis.sadd('genre_to_update', genre)
            logger.info(
                'There are %d genres need to be updated',
                len(genres),
            )
            return movies_need_to_update, genres, persons

        logger.info('There are no movies for update')
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
    def extract_filmwork_data(
        self,
        movies: list,
    ) -> Generator:
        """
        Extract whole movies information from the PostgreSQL database.

        Args:
            movies: list of movies ids to extract from the PostgreSQL database.

        Yields:
            Dictionary mapping movies information.
        """
        with self.pg_connection.cursor() as pg_cursor:
            for movie in movies:
                pg_cursor.execute(
                    """
                    SELECT
                        filmwork.id AS filmwork_id,
                        filmwork.title,
                        filmwork.description,
                        filmwork.rating,
                        filmwork.file_path,
                        filmwork.type,
                        filmwork.creation_date,
                        filmwork.updated_at,
                        COALESCE (
                            json_agg(
                                DISTINCT jsonb_build_object(
                                    'person_role', person_film_work.role,
                                    'person_id', person.id,
                                    'person_name', person.full_name
                                )
                            ) FILTER (WHERE person.id is not null),
                            '[]'
                        ) as persons,
                        COALESCE (
                            json_agg(
                                DISTINCT jsonb_build_object(
                                    'genre_id', genre.id,
                                    'genre_name', genre.name
                                )
                            ) FILTER (WHERE genre.id is not null),
                            '[]'
                        ) as genres
                    FROM film_work as filmwork
                    LEFT JOIN 
                        genre_film_work as genre_film_work 
                            ON 
                        filmwork.id = genre_film_work.film_work_id
                    LEFT JOIN 
                        genre as genre 
                            ON 
                        genre.id = genre_film_work.genre_id
                    LEFT JOIN 
                        person_film_work as person_film_work 
                            ON 
                        filmwork.id = person_film_work.film_work_id
                    LEFT JOIN 
                        person as person 
                            ON 
                        person.id = person_film_work.person_id
                    WHERE filmwork.id = '{0}'
                    GROUP BY filmwork.id
                    ORDER BY updated_at
                    """.format(
                        movie,
                    ),
                )
                film_work_data = dict(pg_cursor.fetchall()[0])
                yield film_work_data

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
    def extract_genre_data(self, genres: list) -> Generator:
        """
        Extract whole genre information from the PostgreSQL database.

        Args:
            genres: list of genres ids to extract from the PostgreSQL database.

        Yields:
            Dictionary mapping genres information.
        """
        with self.pg_connection.cursor() as pg_cursor:
            for genre in genres:
                pg_cursor.execute(
                    """
                    SELECT
                        genre.id AS genre_id,
                        genre.name AS genre_name,
                        genre.description AS genre_description
                    FROM
                        genre
                    WHERE genre.id = '{0}'
                    """.format(
                        genre,
                    ),
                )
                genre_data = dict(pg_cursor.fetchall()[0])
                yield genre_data
