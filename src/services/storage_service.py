from abc import ABC, abstractmethod
from uuid import UUID
from services.film import ElasticFilmService, get_elastic_film_service

# from services.genre import GenreService
# from services.persons import PersonService
from fastapi import Depends

# from api.v1.utils import PaginateQueryParams


# class MovieService(ABC):

#     # def __init__(self, service_type: str, storage: DataStorageInterface):
#     #     self.service = self.create_service(service_type)
#     #     self.storage = storage

#     # @abstractmethod
#     # def create_service(self, service_type: str):
#     #     pass

#     # def __init__(self, service_type: str, storage: DataStorageInterface):
#     #     self.storage = storage
#     # if service_type == 'film':
#     #     self.service = ElasticFilmService()
#     # if service_type == 'genre':
#     #     self.service = GenreService(storage=self.storage)
#     # if service_type == 'persons':
#     #     self.service = PersonService(storage=self.storage)

#     @abstractmethod
#     async def get_by_id(self, id: UUID) -> dict:
#         pass

#     @abstractmethod
#     async def search_data(
#         self,
#         parameters: PaginateQueryParams,
#         query: str = None,
#         sort: str = None,
#         filter: UUID = None,
#     ) -> list:
#         pass


def get_film_service(
    film_service: ElasticFilmService = Depends(get_elastic_film_service),
):
    return film_service
