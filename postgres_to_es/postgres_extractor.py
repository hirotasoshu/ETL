from typing import Iterator, Optional, Tuple

import backoff
import psycopg2
from psycopg2.extensions import connection as pg_conn
from psycopg2.extras import DictCursor

from config import BACKOFF_CONFIG, PostgresDsn
from models import MoviesES


class PostgresExtractor:
    def __init__(
        self,
        dsn: PostgresDsn,
        postgres_connection: Optional[pg_conn] = None,
    ) -> None:
        self._dsn = dsn
        self._postgres_connection = postgres_connection

    @property
    def postgres_connection(self) -> pg_conn:
        """Создает новый объект сессии, если он еще не инициализирован либо закрыт"""

        if self._postgres_connection is None or self._postgres_connection.closed:
            self._postgres_connection = self._create_connection()

        return self._postgres_connection

    @backoff.on_exception(**BACKOFF_CONFIG)
    def _create_connection(self) -> pg_conn:
        """Закрывает старый коннект и создает новый объект сессии"""
        if self._postgres_connection is not None:
            self._postgres_connection.close()

        return psycopg2.connect(**self._dsn.dict(), cursor_factory=DictCursor)

    @backoff.on_exception(**BACKOFF_CONFIG)
    def _extract_movies_data(
        self, query: str, itersize: int
    ) -> Iterator[Tuple[dict, str]]:
        """Возвращает итератор данных в нужном формате для ES"""
        cur = self.postgres_connection.cursor()
        cur.itersize = itersize
        cur.execute(query)

        for row in cur:
            movie = MoviesES(**row).dict()
            # NOTE: костыль, чтобы айди в ES и PG совпадали
            # и работал поиск по id из пг
            movie["_id"] = movie["id"]
            yield movie, str(row["updated_at"])

    def extract_data(
        self, index: str, query: str, itersize: int
    ) -> Iterator[Tuple[dict, str]]:
        if index == "movies":
            return self._extract_movies_data(query, itersize)

        # Так можно добавить другие индексы

        raise ValueError(f"No extract process for index {index}")
