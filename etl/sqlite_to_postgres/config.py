"""Module for configuration settings validation."""

from pydantic import BaseSettings, Field
from dotenv import load_dotenv

load_dotenv()


def to_lower(string: str) -> str:
    """
    Help to convert env variables to lower case.

    Args:
        string: str - string to convert to lower case

    Returns:
        string in lower case.
    """
    return string.lower()


class PostgresSettings(BaseSettings):
    """Settings for PostgreSQL."""

    USER: str
    PASSWORD: str
    HOST: str
    PORT: int
    DB: str = Field(alias='dbname')
    OPTIONS: str

    class Config:
        """Configuration class for correct env variables insertion."""

        env_prefix = 'POSTGRES_'
        alias_generator = to_lower
