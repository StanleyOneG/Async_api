import asyncio
from http import HTTPStatus
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel

from cache.redis_cache import cache
from models.person import PersonWithFilms
from services.film import Film, FilmBase, FilmService, get_film_service
from services.persons import PersonService, get_person_service
from .schemas import Person
from .utils import PaginateQueryParams

router = APIRouter()


async def get_film_by_id(
    film_work_id: UUID,
    film_service: FilmService,
    model: Film | FilmBase,
):
    film = await film_service.get_by_id(film_work_id, model)
    return film


async def get_person_related_films(
    film_service: FilmService,
    person: PersonWithFilms,
    model: Film | FilmBase,
) -> list:
    films = []
    tasks = []
    for item in person.film_work_ids:
        task = asyncio.create_task(get_film_by_id(item, film_service, model))
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
            if actor.uuid == person.uuid:
                roles.append('actor')
        for writer in writers:
            if writer.uuid == person.uuid:
                roles.append('writer')
        for director in directors:
            if director.uuid == person.uuid:
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
@cache
async def search_persons(
    request: Request,
    query: str = Query(default=None),
    paginate_query_params: PaginateQueryParams = Depends(),
    person_service: PersonService = Depends(get_person_service),
    film_service: FilmService = Depends(get_film_service),
):
    persons = await person_service.get_persons_search(
        query,
        paginate_query_params,
        # person_service.elastic_index,
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
                uuid=person.uuid,
                full_name=person.full_name,
                films=await get_person_related_films(
                    film_service, person, Film
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
@cache
async def films_by_person(
    request: Request,
    person_id: UUID,
    person_service: PersonService = Depends(get_person_service),
    film_service: FilmService = Depends(get_film_service),
):
    model = person_service.model
    person = await person_service.get_by_id(person_id, model)
    if not person:
        return []
    related_films = await get_person_related_films(
        film_service, person, FilmBase
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
@cache
async def person_detail(
    request: Request,
    person_id: UUID,
    person_service: PersonService = Depends(get_person_service),
    film_service: FilmService = Depends(get_film_service),
):
    model = person_service.model
    person = await person_service.get_by_id(person_id, model)
    if not person:
        return []

    return Person(
        uuid=person.uuid,
        full_name=person.full_name,
        films=await get_person_related_films(film_service, person, Film),
    )
