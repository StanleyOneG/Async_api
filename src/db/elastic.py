from typing import Optional
from elasticsearch import AsyncElasticsearch
from services.elastic_service import ElasticService

es: Optional[AsyncElasticsearch] = None

# Функция понадобится при внедрении зависимостей
def get_elastic() -> ElasticService:
    return ElasticService(es)
