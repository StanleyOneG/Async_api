import asyncio
from http import HTTPStatus
from typing import Any, Union, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from models.person import PersonWithFilms
from services.film import FilmService, get_film_service, Film, FilmBase


from services.persons import PersonService, get_person_service

router = APIRouter()


class Person(BaseModel):
    uuid: UUID | Any
    full_name: str
    films: list | Any


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


@router.get('/search',
            summary="Поиск участников",
            description="Поиск участников",
            response_description="Список найденных участников",
            tags=["Участники"])
async def search_persons(
    query: str = Query(default=None),
    page: int = Query(default=None, alias='page_number', ge=0),
    size: int = Query(default=None, alias='page_size', ge=1, le=500),
    person_service: PersonService = Depends(get_person_service),
    film_service: FilmService = Depends(get_film_service),
):
    persons = await person_service.get_persons_search(
        query,
        page,
        size,
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


@router.get('/{person_id}/film',
            summary="Кинопроизведения по выбранному участнику",
            description="Кинопроизведения по выбранному участнику",
            response_description="Кинопроизведения по выбранному участнику",
            tags=["Участники"])
async def films_by_person(
    person_id: UUID,
    person_service: PersonService = Depends(get_person_service),
    film_service: FilmService = Depends(get_film_service),
):
    person = await person_service.get_by_id(person_id)
    if not person:
        return []
    related_films = await get_person_related_films(
        film_service, person, FilmBase
    )
    return related_films


@router.get('/{person_id}',
            summary="Участник",
            description="Детали участаника",
            response_description="Детали учатсника",
            tags=["Участники"],
            response_model=Person)
async def person_detail(
    person_id: UUID,
    person_service: PersonService = Depends(get_person_service),
    film_service: FilmService = Depends(get_film_service),
):
    person = await person_service.get_by_id(person_id)
    if not person:
        return []

    return Person(
        uuid=person.uuid,
        full_name=person.full_name,
        films=await get_person_related_films(film_service, person, Film),
    )
