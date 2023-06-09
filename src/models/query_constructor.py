from uuid import UUID
from pydantic import BaseModel, Field
from api.v1.utils import PaginateQueryParams


class QueryConstructor(BaseModel):
    paginate_query_params: PaginateQueryParams
    query: str | None = Field(default=None)
    sort: str | None = Field(default=None)
    filter_genre: UUID = Field(default=None)

    class Config:
        arbitrary_types_allowed = True

    def get_persons_query(self):
        return {
            "match": {"full_name": {"query": self.query, "fuzziness": "AUTO"}}
        }

    def get_films_query(self):
        return {"match": {"title": {"query": self.query, "fuzziness": "AUTO"}}}

    def construct_query(self, elastic_index: str):
        query_body = {}

        if self.paginate_query_params.page_number:
            query_body['from'] = self.paginate_query_params.page_number

        if self.paginate_query_params.page_size:
            query_body["size"] = self.paginate_query_params.page_size

        if self.query:
            find_query = {
                'persons': self.get_persons_query,
                'movies': self.get_films_query,
            }

            query_body['query'] = find_query[elastic_index]()
        return query_body

    def construct_films_list_query(self):
        query_body = {"query": {}}
        if not self.filter_genre:
            query_body['query']["match_all"] = {}
        if self.sort:
            query_body['sort'] = {"imdb_rating": {"order": "desc"}}
        if self.paginate_query_params:
            if self.paginate_query_params.page_size:
                query_body['size'] = self.paginate_query_params.page_size
            if self.paginate_query_params.page_number:
                query_body['from'] = self.paginate_query_params.page_number
        if self.filter_genre:
            query_body['query'] = {
                "query": {
                    "constant_score": {
                        "filter": {"term": {"genre.uuid": self.filter_genre}}
                    }
                }
            }
        return query_body
