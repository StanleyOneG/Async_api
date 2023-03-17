from fastapi import Query


class FilmCommonQueryParams:
    def __init__(self,
                page: int = Query(default=0, alias='page_number', ge=0),
                size: int = Query(default=50,
                                  alias='page_size',
                                  ge=1,
                                  le=1000)):
        self.page = page
        self.size = size
