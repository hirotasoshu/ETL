import logging
import time
from typing import Iterator, Optional, Tuple

import backoff
from elasticsearch import Elasticsearch, helpers
from state import State

from config import BACKOFF_CONFIG, ElasticConfig

logger = logging.getLogger(__name__)


class ElasticLoader:
    def __init__(
        self,
        config: ElasticConfig,
        state: State,
        elastic_connection: Optional[Elasticsearch] = None,
    ) -> None:
        self._config = config
        self._elastic_connection = elastic_connection
        self._state = state

    @property
    def elastic_connection(self) -> Elasticsearch:
        """Вернуть текущее подключение для ES или инициализировать новое"""
        if self._elastic_connection is None or not self._elastic_connection.ping():
            self._elastic_connection = self._create_connection()

        return self._elastic_connection  # type: ignore

    @backoff.on_exception(**BACKOFF_CONFIG)
    def _create_connection(self) -> Elasticsearch:
        """Создать новое подключение для ES"""
        return Elasticsearch([f"{self._config.host}:{self._config.port}"])

    @backoff.on_exception(**BACKOFF_CONFIG)
    def _generate_docs(
        self, data: Iterator[Tuple[dict, str]], itersize: int
    ) -> Iterator[dict]:
        """
        Возвращает итератор документов для ES.
        Так же во время продуцирования фильмов записывает в стейт updated_at
        каждого n-го фильма (n=itersize)
        После продуцирования всех фильмов записывает в стейт последний updated_at
        """
        i = 0
        last_updated_at = ""

        for movie, updated_at in data:
            i += 1
            last_updated_at = updated_at

            yield movie

            if i % itersize == 0:
                self._state.set_key("load_from", last_updated_at)

        self._state.set_key("load_from", last_updated_at)

    @backoff.on_exception(**BACKOFF_CONFIG)
    def upload_data(self, data: Iterator[Tuple[dict, str]], itersize: int) -> None:
        """Загружает данные в ES используя итератор"""
        t = time.perf_counter()

        docs_generator = self._generate_docs(data, itersize)

        lines, _ = helpers.bulk(
            client=self.elastic_connection,
            actions=docs_generator,
            index=self._config.index,
            chunk_size=itersize,
        )

        elapsed = time.perf_counter() - t

        if lines == 0:
            logger.info("Nothing to update")
        else:
            logger.info("%s lines saved in %s", lines, elapsed)
