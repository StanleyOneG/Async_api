from uuid import UUID
from pydantic import BaseSettings, Field, FilePath
from dotenv import load_dotenv

load_dotenv()


class TestSettings(BaseSettings):
    es_host: str = Field(..., env='ELASTIC_TEST_HOST')
    es_port: int = Field(..., env='ELASTIC_PORT')
    es_user: str = Field(..., env='ELASTIC_USERNAME')
    es_password: str | int = Field(..., env='ELASTIC_PASSWORD')
    es_movies_index: str = Field(default='movies')
    es_persons_index: str = Field(default='persons')
    es_genres_index: str = Field(default='genres')
    es_id_field: str = Field(..., env='ES_ID')
    es_movies_index_mapping: FilePath = Field(
        default='testdata/es_movies_schema.json'
    )
    es_persons_index_mapping: FilePath = Field(
        default='testdata/es_persons_schema.json'
    )
    es_genres_index_mapping: FilePath = Field(
        default='testdata/es_genres_schema.json'
    )

    redis_host: str = Field(..., env='REDIS_TEST_HOST')
    service_url: str = Field(..., env='SERVICE_URL')


class EsIndexes:
    """Helper class for es_indexes iteration."""

    def __init__(self, es_index_names: list, es_index_mappings: list):
        self.index_names = es_index_names
        self.index_mappings = es_index_mappings

    def __aiter__(self):
        self.inames = iter(self.index_names)
        self.imappings = iter(self.index_mappings)
        return self

    async def __anext__(self):
        try:
            index_name = next(self.inames)
            index_map = next(self.imappings)
        except StopIteration:
            raise StopAsyncIteration

        return index_name, index_map


test_settings = TestSettings()

index_mappings = [
    test_settings.es_movies_index_mapping,
    test_settings.es_persons_index_mapping,
    test_settings.es_genres_index_mapping,
]

index_names = [
    test_settings.es_movies_index,
    test_settings.es_persons_index,
    test_settings.es_genres_index,
]

test_indexes = EsIndexes(index_names, index_mappings)
