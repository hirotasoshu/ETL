from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel


class Person(BaseModel):
    id: UUID
    name: str


class MoviesES(BaseModel):
    id: UUID
    imdb_rating: Optional[float] = None
    genre: Optional[str] = None
    title: str
    description: Optional[str] = None
    director: Optional[List[str]] = None
    actors_names: Optional[List[str]] = None
    writers_names: Optional[List[str]] = None
    actors: Optional[List[Person]] = None
    writers: Optional[List[Person]] = None
