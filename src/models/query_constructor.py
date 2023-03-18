from uuid import UUID
from pydantic import BaseModel, Field


class QueryConstructor(BaseModel):

    page: int
    size: int
    query: str | None = Field(default=None)
    sort: str | None = Field(default=None)
    filter_genre: UUID | None = Field(default=None)

    def get_persons_query(self):
        return {
            "match": {"full_name": {"query": self.query, "fuzziness": "AUTO"}}
        }

    def get_films_query(self):
        return {"match": {"title": {"query": self.query, "fuzziness": "AUTO"}}}

    def construct_query(self, elastic_index: str):
        query_body = {}

        if self.page:
            query_body['from'] = self.page

        if self.size:
            query_body["size"] = self.size

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
        if self.size:
            query_body['size'] = self.size
        if self.page:
            query_body['from'] = self.page
        if self.filter_genre:
            query_body['query'] = {
                "nested": {
                    "path": "genre",
                    "query": {
                        "bool": {
                            "should": [
                                {"match": {"genre.uuid": self.filter_genre}}
                            ]
                        }
                    }
                }
            }
        return query_body
