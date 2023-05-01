"""Module for validating configuration parameters."""

from dotenv import load_dotenv
from pydantic import BaseSettings

load_dotenv()


def to_lower(value: str) -> str:
    """Helper to convert env variables to lower case

    Args:
        value: str - string to be converted to lower case

    Returns:
        converted to lower case value
    """
    return value.lower()


class ProjectSettings(BaseSettings):
    NAME: str
    DESCRIPTION: str
    VERSION: str
    CACHE_SERVICE_NAME: str

    class Config:
        """Configuration class for correct env variables insertion."""

        env_prefix = 'PROJECT_'
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
        alias_generator = to_lower


class RedisSettings(BaseSettings):
    """Configuration for Redis."""

    API_HOST: str
    PORT: int
    EXPIRE: int

    class Config:
        """Configuration class for correct env variables insertion."""

        env_prefix = 'REDIS_CACHE_'
        alias_generator = to_lower


class JwtSettings(BaseSettings):
    """Configuration for Redis."""

    PUBLIC_KEY: str

    class Config:
        """Configuration class for correct env variables insertion."""

        env_prefix = 'JWT_'
        alias_generator = to_lower


class Settings(BaseSettings):
    """Helper class for configuration access."""

    ELASTICSEARCH = ElasticSettings()
    REDIS = RedisSettings()
    PROJECT = ProjectSettings()
    JWT = JwtSettings()
