from elasticsearch import AsyncElasticsearch

from services.elastic_service import ElasticSearvice

storage: AsyncElasticsearch = None


def get_storage():
    return ElasticSearvice(storage_client=storage)
