from elasticsearch import AsyncElasticsearch

from services.elastic_service import ElasticService

storage: AsyncElasticsearch = None


def get_storage():
    return ElasticService(storage_client=storage)
