from http import HTTPStatus
from typing import Union, List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from services.film import FilmService, get_film_service

from models.genre import Genre
from models.film import PersonBase

router = APIRouter()


class Person(BaseModel):
    uuid: str
    full_name: str