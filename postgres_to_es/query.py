from typing import Optional


def get_query(load_from: Optional[str]) -> str:
    """
    Формирует sql запрос с подставленной временной меткой
    """
    if not load_from:
        raise ValueError(
            "Для получения sql запроса нужна временная метка, сконвертированная в строку"
        )

    return f"""
SELECT film.id,
    film.rating AS imdb_rating,
    STRING_AGG(DISTINCT genre.name, ' ') AS genre,
    film.title,
    film.description,
    ARRAY_AGG(DISTINCT person.full_name) FILTER (WHERE person_film.role = 'director') AS director,
    ARRAY_AGG(DISTINCT person.full_name) FILTER (WHERE person_film.role = 'actor') AS actors_names,
    ARRAY_AGG(DISTINCT person.full_name) FILTER (WHERE person_film.role = 'writer') AS writers_names,
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
