from typing import Iterator, Optional

import backoff
import psycopg2
from models import MoviesES
from psycopg2.extensions import connection as pg_conn
from psycopg2.extras import DictCursor
from state import State

from config import BACKOFF_CONFIG, PostgresDsn


class PostgresExtractor:
    def __init__(
        self,
        dsn: PostgresDsn,
        state: State,
        postgres_connection: Optional[pg_conn] = None,
    ) -> None:
        self._dsn = dsn
        self._state = state
        self._postgres_connection = postgres_connection

    @property
    def postgres_connection(self) -> pg_conn:
        """Создает новый объект сессии, если он еще не инициализирован либо закрыт"""

        if self._postgres_connection and not self._postgres_connection.closed:
            pass
        else:
            self._postgres_connection = self._create_connection()

        return self._postgres_connection

    @backoff.on_exception(**BACKOFF_CONFIG)
    def _create_connection(self) -> pg_conn:
        """Создает новый объект сессии"""

        return psycopg2.connect(**self._dsn.dict(), cursor_factory=DictCursor)

    @backoff.on_exception(**BACKOFF_CONFIG)
    def extract_data(self, query: str, itersize: int) -> Iterator[dict]:
        """Возвращает итератор данных в нужном формате для ES"""
        cur = self.postgres_connection.cursor()
        cur.itersize = itersize
        cur.execute(query)

        for row in cur:
            yield MoviesES(**row).dict()
            self._state.set_key("load_from", str(row["updated_at"]))
