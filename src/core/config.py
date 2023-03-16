import os
from logging import config as logging_config
from .backend_conf import Settings

from core.logger import LOGGING

logging_config.dictConfig(LOGGING)

configs = Settings()

PROJECT_NAME = os.getenv('PROJECT_NAME', 'movies')
PROJECT_DESCRIPTION = os.getenv('PROJECT_DESCRIPTION', 'Movies description')
PROJECT_VERSION = os.getenv('PROJECT_VERSION', "1.0.0")

REDIS_CACHE_HOST = configs.REDIS.API_HOST
REDIS_CACHE_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_CACHE_EXPIRE = int(os.getenv('REDIS_CACHE_EXPIRE', 300))

ELASTIC_HOST = configs.ELASTICSEARCH.HOST
ELASTIC_PORT = configs.ELASTICSEARCH.PORT
ELASTIC_USERNAME = configs.ELASTICSEARCH.USERNAME
ELASTIC_PASSWORD = configs.ELASTICSEARCH.PASSWORD

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
