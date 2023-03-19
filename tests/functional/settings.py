from uuid import UUID
from pydantic import BaseSettings, Field, FilePath
from dotenv import load_dotenv

load_dotenv()


class TestSettings(BaseSettings):
    es_host: str = Field('http://127.0.0.1:9200', env='ELASTIC_TEST_HOST')
    es_port: int = Field(..., env='ELASTIC_PORT')
    es_user: str = Field(..., env='ELASTIC_USERNAME')
    es_password: str|int = Field(..., env='ELASTIC_PASSWORD')
    es_index: str = Field(..., env='ELASTIC_INDEX')
    es_id_field: str = Field(..., env='ES_ID')
    es_index_mapping: FilePath = Field(default='es_movies_schema.json')

    redis_host: str = Field(..., env='REDIS_TEST_HOST')
    service_url: str = Field(..., env='SERVICE_URL')


test_settings = TestSettings()
