import asyncio
from http import HTTPStatus
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request

from api.v1.schemas import Person
from api.v1.utils import PaginateQueryParams
from cache.redis_cache import cache
from models.film import Film, FilmBase
from models.person import PersonWithFilms
from services.base_service import MovieService
from services.storage_service import get_film_service, get_persons_service
from auth.jwt import check_auth

router = APIRouter()


async def get_film_by_id(
    film_work_id: UUID,
    film_service: MovieService,
    model: Film | FilmBase,
) -> Film | FilmBase:
    film_dict_from_storage = await film_service.get_by_id(id=film_work_id)
    film = model(**film_dict_from_storage)
    return film


async def get_person_related_films(
    film_service: MovieService,
    person: PersonWithFilms,
    model: Film | FilmBase,
) -> list:
    films = []
    tasks = []
    for item in person.get('film_work_ids'):
        task = asyncio.create_task(
            get_film_by_id(
                film_work_id=item,
                film_service=film_service,
                model=model,
            )
        )
        tasks.append(task)

    for task in asyncio.as_completed(tasks):
        film = await task
        films.append(film)

    if model == FilmBase:
        return films

    related_movies = []
    for film_work_id, actors, writers, directors in [
        (film.uuid, film.actors, film.writers, film.directors)
        for film in films
    ]:
        roles = []
        for actor in actors:
            if str(actor.uuid) == person.get('uuid'):
                roles.append('actor')
        for writer in writers:
            if str(writer.uuid) == person.get('uuid'):
                roles.append('writer')
        for director in directors:
            if str(director.uuid) == person.get('uuid'):
                roles.append('director')
        related_movies.append(dict(uuid=film_work_id, roles=roles))
    return related_movies


@router.get(
    '/search',
    summary="Поиск участников",
    description="Поиск участников",
    response_description="Список найденных участников",
    tags=["Полнотекстовый поиск"],
    response_model=List[Person],
)
@check_auth(endpoint_permission='subscriber')
@cache
async def search_persons(
    request: Request,
    query: str = Query(default=None),
    paginate_query_params: PaginateQueryParams = Depends(),
    person_service: MovieService = Depends(get_persons_service),
    film_service: MovieService = Depends(get_film_service),
):
    persons = await person_service.search_data(
        query=query,
        parameters=paginate_query_params,
    )
    if not persons:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='persons not found',
        )
    result = []
    for person in persons:
        result.append(
            Person(
                uuid=person.get('uuid'),
                full_name=person.get('full_name'),
                films=await get_person_related_films(
                    film_service=film_service,
                    person=person,
                    model=Film,
                ),
            )
        )
    return result


@router.get(
    '/{person_id}/film',
    summary="Кинопроизведения по выбранному участнику",
    description="Кинопроизведения по выбранному участнику",
    response_description="Кинопроизведения по выбранному участнику",
    tags=["Участники"],
    response_model=List[FilmBase],
)
@check_auth(endpoint_permission='subscriber')
@cache
async def films_by_person(
    request: Request,
    person_id: UUID,
    person_service: MovieService = Depends(get_persons_service),
    film_service: MovieService = Depends(get_film_service),
):
    person = await person_service.get_by_id(id=person_id)
    if not person:
        return []
    related_films = await get_person_related_films(
        film_service=film_service,
        person=person,
        model=FilmBase,
    )
    return related_films


@router.get(
    '/{person_id}',
    summary="Участник",
    description="Детали участаника",
    response_description="Детали учатсника",
    tags=["Участники"],
    response_model=Person,
)
@check_auth(endpoint_permission='subscriber')
@cache
async def person_detail(
    request: Request,
    person_id: UUID,
    persons_service: MovieService = Depends(get_persons_service),
    film_service: MovieService = Depends(get_film_service),
) -> Person:
    person = await persons_service.get_by_id(id=person_id)
    if not person:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='person not found'
        )

    return Person(
        uuid=person.get('uuid'),
        full_name=person.get('full_name'),
        films=await get_person_related_films(
            film_service=film_service,
            person=person,
            model=Film,
        ),
    )
