"""Module for validating configuration parameters."""

from pydantic import BaseSettings, Field
from dotenv import load_dotenv

load_dotenv()


class ElasticSettings(BaseSettings):
    """Configuration for Elasticsearch."""

    API_HOST: str = Field(alias='host')
    PORT: int
    USERNAME: str
    PASSWORD: str

    class Config:
        """Configuration class for correct env variables insertion."""

        env_prefix = 'ELASTIC_'


class RedisSettings(BaseSettings):
    """Configuration for Redis."""

    API_HOST: str

    class Config:
        """Configuration class for correct env variables insertion."""

        env_prefix = 'REDIS_CACHE_'


class Settings(BaseSettings):
    """Helper class for configuration access."""

    ELASTICSEARCH = ElasticSettings()
    REDIS = RedisSettings()
