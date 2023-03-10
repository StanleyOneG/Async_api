"""Module for starting ETL pipeline."""


import logging
from datetime import datetime
from time import sleep
from typing import NoReturn

import backoff
import dotenv
import elasticsearch
import psycopg2
from extract import ExtractorFromPostgres
from load import ElasticLoader
from psycopg2.errors import InterfaceError
from psycopg2.extras import DictCursor
from redis import Redis
from redis.exceptions import ConnectionError
from transform import Transformer
from backend_conf import Settings
from contextlib import closing

dotenv.load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CHUNK_SIZE = 100
CHECK_FREQUENCY = 30


def etl_process(
    extractor: ExtractorFromPostgres,
    transformer: Transformer,
    loader: ElasticLoader,
    redis: Redis,
) -> NoReturn:
    """
    Process the ETL pipeline in cycle.

    Args:
        extractor: ExtractorFromPostgres - Class check and extract data
        transformer: Transformer - Class to transform persons data
        loader: ElasticLoader - Class to load data to Elasticsearch index
        redis: Redis - Redis connection
    """
    while True:
        try:
            if redis.get('person_last_checked') is None:
                person_last_checked: datetime = datetime(1970, 1, 1)
            else:
                date_from_redis = redis.get('person_last_checked')
                person_last_checked: datetime = datetime.strptime(
                    date_from_redis.decode('utf-8'),
                    '"%Y-%m-%d %H:%M:%S.%f+00:00"',
                )
                logger.info('person_last_checked %s', person_last_checked)
            if extractor.find_tables_updates(person_last_checked) is not None:
                persons_id = [
                    person.decode('utf-8')
                    for person in redis.smembers('persons_need_to_update')
                ]
                loader.load_data(
                    transformer.prepare_for_es(
                        extractor.extract_person_data(persons_id),
                    ),
                )
                redis.srem('persons_need_to_update', *persons_id)
            logger.info('Next check in %d sec', CHECK_FREQUENCY)
            sleep(CHECK_FREQUENCY)
        except Exception as pipeline_error:
            logger.error(
                '%s\n\nRetrying in %d sec',
                pipeline_error,
                CHECK_FREQUENCY,
            )
            sleep(CHECK_FREQUENCY)


@backoff.on_exception(
    backoff.expo,
    (
        InterfaceError,
        ConnectionError,
        elasticsearch.exceptions.ConnectionError,
    ),
)
def main() -> NoReturn:
    """Init the backend connections to databases and start ETL pipeline."""
    settings = Settings()

    with Redis(host=settings.REDIS.HOST) as redis_conn:
        with closing(
            psycopg2.connect(
                **settings.POSTGRES.dict(by_alias=True),
                cursor_factory=DictCursor,
            ),
        ) as pg_conn:
            with elasticsearch.Elasticsearch(
                [
                    {
                        'host': settings.ELASTICSEARCH.HOST,
                        'port': settings.ELASTICSEARCH.PORT,
                    },
                ],
                http_auth=(
                    settings.ELASTICSEARCH.USERNAME,
                    settings.ELASTICSEARCH.PASSWORD,
                ),
            ) as elastic:
                extractor = ExtractorFromPostgres(
                    pg_connection=pg_conn,
                    redis=redis_conn,
                )
                transformer = Transformer(redis_conn)
                loader = ElasticLoader(
                    elastic,
                    index_info='es_schema.json',
                    redis=redis_conn,
                    chunk_size=CHUNK_SIZE,
                )
                etl_process(
                    extractor=extractor,
                    transformer=transformer,
                    loader=loader,
                    redis=redis_conn,
                )


if __name__ == '__main__':
    main()
