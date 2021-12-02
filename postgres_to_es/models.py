from enum import Enum
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel


class FilmType(str, Enum):
    movie = "movie"
    tv_show = "tv_show"


class PersonType(str, Enum):
    actor = "actor"
    director = "director"
    writer = "writer"


class AbstractModel(BaseModel):
    id: UUID


class PersonInFilm(AbstractModel):
    name: str


class GenresES(AbstractModel):
    name: str


class PersonsES(AbstractModel):
    name: str
    role: Optional[List[PersonType]] = None
    film_ids: Optional[List[UUID]] = None


class MoviesES(AbstractModel):
    title: str
    imdb_rating: Optional[float] = None
    type: FilmType
    description: Optional[str] = None
    genres: Optional[List[GenresES]] = None
    directors: Optional[List[PersonInFilm]] = None
    actors: Optional[List[PersonInFilm]] = None
    writers: Optional[List[PersonInFilm]] = None
    file_path: Optional[str] = None
