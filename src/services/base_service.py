from abc import ABC, abstractmethod
from uuid import UUID

from api.v1.utils import PaginateQueryParams


class MovieService(ABC):
    @abstractmethod
    async def get_by_id(self, id: UUID) -> dict:
        pass

    @abstractmethod
    async def search_data(
        self,
        parameters: PaginateQueryParams = None,
        query: str = None,
        sort: str = None,
        filter: UUID = None,
    ) -> list:
        pass
