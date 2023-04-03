from fastapi import Depends

from services.film import ElasticFilmService, get_elastic_film_service
from services.persons import ElasticPersonsService, get_elastic_persons_service


def get_film_service(
    film_service: ElasticFilmService = Depends(get_elastic_film_service),
):
    return film_service


def get_persons_service(
    persons_service: ElasticPersonsService = Depends(
        get_elastic_persons_service
    ),
):
    return persons_service
