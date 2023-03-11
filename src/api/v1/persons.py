import asyncio
from http import HTTPStatus
from typing import Any, Union, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from services.film import FilmService, get_film_service


from services.persons import PersonService, get_person_service

router = APIRouter()


class Person(BaseModel):
    uuid: UUID
    full_name: str
    films: Any


@router.get('/{person_id}', response_model=Person)
async def person_detail(
    person_id: UUID,
    person_service: PersonService = Depends(get_person_service),
    film_service: FilmService = Depends(get_film_service),
):
    async def get_film_by_id(film_work_id):
        film = await film_service.get_by_id(film_work_id)
        return film

    person = await person_service.get_by_id(person_id)
    films = []
    tasks = []
    for item in person.film_work_ids:
        task = asyncio.create_task(get_film_by_id(item))
        tasks.append(task)

    for task in asyncio.as_completed(tasks):
        film = await task
        films.append(film)

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

    if not person:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='person not found',
        )

    return Person(
        uuid=person.uuid,
        full_name=person.full_name,
        films=related_movies,
    )
