"""Test load_data module."""

import os

import pytest
import sqlite3
import psycopg2
from datetime import datetime
from dotenv import load_dotenv
from psycopg2.extras import DictCursor

load_dotenv()

TABLES = [
    'film_work',
    'genre',
    'person',
    'person_film_work',
    'genre_film_work',
]


@pytest.fixture(autouse=True, scope='session')
def setup():
    """
    Collect environment configuration, open and close databases connection.

    Yields:
        SQLite and PostgreSQL cursor objects.
    """
    sqlite_path = os.environ.get('SQLITE_PATH')
    conf = {
        'dbname': 'POSTGRES_DB',
        'user': 'POSTGRES_USER',
        'password': 'POSTGRES_PASSWORD',
        'host': 'DB_HOST',
        'port': 'DB_PORT',
        'options': 'DB_OPTIONS',
    }
    db_config = {
        conf_key: os.environ.get(
            conf_value,
        )
        for conf_key, conf_value in conf.items()
    }
    # Connect to SQLite database
    sqlite_conn = sqlite3.connect(sqlite_path)
    sqlite_conn.row_factory = sqlite3.Row
    sqlite_cur = sqlite_conn.cursor()
    # connect to PostgreSQL database
    postgres_conn = psycopg2.connect(
        **db_config,
        cursor_factory=DictCursor,
    )
    postgres_cur = postgres_conn.cursor()
    yield postgres_cur, sqlite_cur
    sqlite_conn.close()
    postgres_conn.close()


def zip_dicts(first: dict, second: dict):
    """
    Zip two dictionaries.

    Args:
        first (dict): First dictionary.
        second (dict): Second dictionary.

    Returns:
        dict: Zipped dictionary.
    """
    return zip(first.items(), second.items())


def test_tables_consistency(setup):
    """Rows of two databases should be equal."""
    postgres_cur, sqlite_cur = setup
    for table in TABLES:
        sqlite_cur.execute(f'select * from {table} order by id')
        postgres_cur.execute(f'select * from {table} order by id')
        sqlite_data = [dict(row) for row in sqlite_cur.fetchall()]
        postgres_data = [dict(row) for row in postgres_cur.fetchall()]
        assert len(sqlite_data) == len(postgres_data)
        for sql_dict, pg_dict in zip(sqlite_data, postgres_data):
            for (sql_k, sql_v), (pg_k, pg_v) in zip_dicts(sql_dict, pg_dict):
                if {'created_at', 'updated_at'} & {sql_k, pg_k}:
                    assert (
                        datetime.strptime(
                            ''.join([sql_v, '00']),
                            '%Y-%m-%d %H:%M:%S.%f%z',
                        )
                        == pg_v
                    )
                elif sql_k == pg_k:
                    assert sql_v == pg_v
