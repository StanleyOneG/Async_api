from uuid import UUID

from api.v1.utils import PaginateQueryParams
from models.query_constructor import QueryConstructor


class BaseElasticService:
    async def get_by_id(self, id: UUID):
        data = await self.storage.get_data_by_id(
            index=self.elastic_index,
            id=id,
        )
        return data

    async def search_data(
        self,
        parameters: PaginateQueryParams,
        query: str = None,
        sort: str = None,
        filter: UUID = None,
    ) -> list:
        query_constructor = QueryConstructor(
            query=query,
            sort=sort,
            paginate_query_params=parameters,
        )
        query_body = query_constructor.construct_query(self.elastic_index)
        return await self.storage.search_data(
            query_body=query_body,
            index=self.elastic_index,
        )
