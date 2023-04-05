import os
from logging import config as logging_config

from core.logger import LOGGING

from .backend_conf import Settings

logging_config.dictConfig(LOGGING)

configs = Settings()

PROJECT_NAME = configs.PROJECT.NAME
PROJECT_DESCRIPTION = configs.PROJECT.DESCRIPTION
PROJECT_VERSION = configs.PROJECT.VERSION
CACHE_SERVICE_NAME = configs.PROJECT.CACHE_SERVICE_NAME

REDIS_CACHE_HOST = configs.REDIS.API_HOST
REDIS_CACHE_PORT = configs.REDIS.PORT
REDIS_CACHE_EXPIRE = configs.REDIS.EXPIRE

ELASTIC_HOST = configs.ELASTICSEARCH.HOST
ELASTIC_PORT = configs.ELASTICSEARCH.PORT
ELASTIC_USERNAME = configs.ELASTICSEARCH.USERNAME
ELASTIC_PASSWORD = configs.ELASTICSEARCH.PASSWORD

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
