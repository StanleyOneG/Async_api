from http import HTTPStatus
from typing import Union, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel


from services.persons import PersonService, get_person_service

router = APIRouter()


class Person(BaseModel):
    uuid: UUID
    full_name: str
    role: str | None
    film_ids: list[str] | None


@router.get('/{person_id}', response_model=Person)
async def person_detail(
    person_id: UUID,
    person_service: PersonService = Depends(get_person_service),
):
    person = await person_service.get_by_id(person_id)
    if not person:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='person not found',
        )
    return Person(uuid=person.uuid, full_name=person.full_name)
