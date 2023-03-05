"""Module for loading data from sqlite database to postgresql database."""

import datetime
import logging
import os
import re
import sqlite3
import uuid
from contextlib import closing, contextmanager
from dataclasses import astuple, dataclass, field

import psycopg2
from config import PostgresSettings
from psycopg2.errors import (
    ActiveSqlTransaction,
    InFailedSqlTransaction,
    ProgrammingError,
    UniqueViolation,
)
from psycopg2.extensions import connection as _connection
from psycopg2.extras import DictCursor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TABLES = [
    'film_work',
    'person',
    'genre',
    'person_film_work',
    'genre_film_work',
]

pg_errors = (
    InFailedSqlTransaction,
    ProgrammingError,
    ActiveSqlTransaction,
    UniqueViolation,
)


@dataclass
class FilmWork:
    """Class for movie data."""

    title: str
    description: str
    rating: float
    file_path: str
    type: str
    creation_date: datetime.datetime
    created_at: datetime.datetime = field(
        default_factory=datetime.datetime.now,
    )
    updated_at: datetime.datetime = field(
        default_factory=datetime.datetime.now,
    )
    id: uuid.UUID = field(default_factory=uuid.uuid4)


@dataclass
class Person:
    """Class for person data."""

    full_name: str
    created_at: datetime.datetime = field(
        default_factory=datetime.datetime.now,
    )
    updated_at: datetime.datetime = field(
        default_factory=datetime.datetime.now,
    )
    id: uuid.UUID = field(default_factory=uuid.uuid4)


@dataclass
class Genre:
    """Class for genre data."""

    name: str
    description: str
    created_at: datetime.datetime = field(
        default_factory=datetime.datetime.now,
    )
    updated_at: datetime.datetime = field(
        default_factory=datetime.datetime.now,
    )
    id: uuid.UUID = field(default_factory=uuid.uuid4)


@dataclass
class PersonFilmWork:
    """Class for person film work data."""

    role: str
    person_id: uuid.UUID
    film_work_id: uuid.UUID
    created_at: datetime.datetime = field(
        default_factory=datetime.datetime.now,
    )
    id: uuid.UUID = field(default_factory=uuid.uuid4)


@dataclass
class GenreFilmWork:
    """Class for genre film work data."""

    genre_id: uuid.UUID
    film_work_id: uuid.UUID
    created_at: datetime.datetime = field(
        default_factory=datetime.datetime.now,
    )
    id: uuid.UUID = field(default_factory=uuid.uuid4)


DATA_CLASSES = [FilmWork, Person, Genre, PersonFilmWork, GenreFilmWork]


def load_from_sqlite(
    connection: sqlite3.Connection,
    pg_conn: _connection,
    chunk_size: int,
):
    """
    Load data from SQLite database to PostgreSQL database.

    Args:
        connection (sqlite3.Connection): Connection to SQLite.
        pg_conn (_connection): Connection to PostgreSQL.
        chunk_size (int): Number of rows to load at a time.
    """
    pg_cursor = pg_conn.cursor()
    sqlite_cursor = connection.cursor()
    for table, class_name in zip(TABLES, DATA_CLASSES):
        size = chunk_size
        total_rows = dict(
            sqlite_cursor.execute(
                f"""
                SELECT COUNT(id) FROM {table}
                """,
            ).fetchall()[0],
        )['COUNT(id)']
        logger.info(f'Rows in SQLite {table}: {total_rows}')
        try:
            pg_cursor.execute(f'TRUNCATE TABLE {table} CASCADE')
            logger.info(f'Truncated table {table}')
        except pg_errors as truncate_error:
            logger.error(f'{truncate_error}')
        start_row = 0
        inserted = 0
        while start_row <= total_rows:
            try:
                sqlite_cursor.execute(
                    f"""
                    SELECT * FROM {table}
                    ORDER BY id
                    LIMIT {start_row}, {size}
                    """,
                )
                table_data = []
                for row in sqlite_cursor.fetchall():
                    table_data.append(
                        astuple(
                            class_name(**row),
                        ),
                    )
            except sqlite3.OperationalError as error_msg:
                logger.error(error_msg)

            # Insert into postgres database
            argument_to_insert = '%s,'
            class_fields = class_name.__dataclass_fields__.keys()
            args = ','.join(
                pg_cursor.mogrify(
                    '({0})'.format(argument_to_insert * len(class_fields)),
                    column,
                ).decode()
                for column in table_data
            )
            try:
                pg_cursor.execute(
                    'INSERT INTO {0} {1} VALUES {2}'.format(
                        table,
                        re.sub("'", '', str((*class_fields,))),
                        re.sub(r',\s*\)', ')', args),
                    ),
                )
            except pg_errors as insert_error:
                logger.error(insert_error)
            start_row += size
            inserted += len(table_data)
            logger.info(f'Inserted {table} rows: {inserted}')
        logger.info(f'---------- Finished inserting {table} -------------')


@contextmanager
def conn_context(db_path: str):
    """
    Create and close a connection to sqlite database.

    Args:
        db_path (str): Path to SQLite database.

    Yields:
        sqlite3.Connection: Connection to SQLite database.
    """
    sqlite_conn = sqlite3.connect(db_path)
    sqlite_conn.row_factory = sqlite3.Row
    yield sqlite_conn
    sqlite_conn.close()


def main():
    """Lounch context manager and database migration."""
    # Get configuration from environment
    sqlite_path = os.environ.get('SQLITE_PATH')
    settings = PostgresSettings()
    with conn_context(sqlite_path) as sqlite_conn:
        with closing(
            psycopg2.connect(
                **settings.dict(by_alias=True),
                cursor_factory=DictCursor,
            ),
        ) as pg_conn:
            load_from_sqlite(sqlite_conn, pg_conn, chunk_size=500)
            pg_conn.commit()


if __name__ == '__main__':
    main()
