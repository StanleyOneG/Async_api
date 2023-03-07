"""Module for validating configuration parameters."""

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
    """Configuration for PostgreSQL."""

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


class ElasticSettings(BaseSettings):
    """Configuration for Elasticsearch."""

    HOST: str
    PORT: int
    USERNAME: str
    PASSWORD: str

    class Config:
        """Configuration class for correct env variables insertion."""

        env_prefix = 'ELASTIC_'


class RedisSettings(BaseSettings):
    """Configuration for Redis."""

    HOST: str

    class Config:
        """Configuration class for correct env variables insertion."""

        env_prefix = 'REDIS_'


class Settings(BaseSettings):
    """Helper class for configuration access."""

    POSTGRES = PostgresSettings()
    ELASTICSEARCH = ElasticSettings()
    REDIS = RedisSettings()
