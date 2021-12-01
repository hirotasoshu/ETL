from typing import Optional


def get_movies_query(load_from: Optional[str]) -> str:
    """
    Формирует sql запрос с подставленной временной меткой для индекса movies
    """

    return f"""
SELECT film.id,
    film.rating AS imdb_rating,
    film.title,
    film.description,
    film.file_path,
    film.type,
    ARRAY_AGG(DISTINCT jsonb_build_object('id', genre.id, 'name', genre.name)) AS genres,
    ARRAY_AGG(DISTINCT jsonb_build_object('id', person.id, 'name', person.full_name)) FILTER (WHERE person_film.role = 'director') AS directors,
    ARRAY_AGG(DISTINCT jsonb_build_object('id', person.id, 'name', person.full_name)) FILTER (WHERE person_film.role = 'actor') AS actors,
    ARRAY_AGG(DISTINCT jsonb_build_object('id', person.id, 'name', person.full_name)) FILTER (WHERE person_film.role = 'writer') AS writers,
    GREATEST(film.updated_at, MAX(person.updated_at), MAX(genre.updated_at)) AS updated_at
FROM content.film_work film
    LEFT JOIN content.genre_film_work AS genre_film ON film.id = genre_film.film_work_id
    LEFT JOIN content.genre AS genre ON genre_film.genre_id = genre.id
    LEFT JOIN content.person_film_work AS person_film ON film.id = person_film.film_work_id
    LEFT JOIN content.person AS person ON person_film.person_id = person.id
WHERE
    GREATEST(film.updated_at, person.updated_at, genre.updated_at) > '{load_from}'
GROUP BY film.id
ORDER BY GREATEST(film.updated_at, MAX(person.updated_at), MAX(genre.updated_at)) ASC
    """


def get_genres_query(load_from: Optional[str]) -> str:
    """
    Формирует sql запрос с подставленной временной меткой для индекса genres
    """

    return f"""
SELECT genre.id,
    genre.name,
    genre.updated_at
FROM content.genre genre
WHERE
    genre.updated_at > '{load_from}'
GROUP BY genre.id
ORDER BY genre.updated_at ASC
    """


def get_persons_query(load_from: Optional[str]) -> str:
    """
    Формирует sql запрос с подставленной временной меткой для индекса persons
    """
    ...


def get_query_by_index(index: str, load_from: Optional[str]) -> str:
    """Формирует нужный sql запрос в зависимости от индекса"""

    if not load_from:
        raise ValueError("For getting sql query datetime string required")

    elif index == "movies":
        return get_movies_query(load_from)

    elif index == "genres":
        return get_genres_query(load_from)

    # можно добавить таким образом остальные индексы

    raise ValueError(f"No query for index {index}")
