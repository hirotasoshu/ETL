import logging
import time
from typing import Iterator, Optional

import backoff
from elasticsearch import Elasticsearch, helpers

from config import BACKOFF_CONFIG, ElasticConfig

logger = logging.getLogger(__name__)


class ElasticLoader:
    def __init__(
        self, config: ElasticConfig, elastic_connection: Optional[Elasticsearch] = None
    ) -> None:
        self._config = config
        self._elastic_connection = elastic_connection

    @property
    def elastic_connection(self) -> Elasticsearch:
        """Вернуть текущее подключение для ES или инициализировать новое"""
        if self._elastic_connection and self._elastic_connection.ping():
            pass
        else:
            self._elastic_connection = self._create_connection()

        return self._elastic_connection  # type: ignore

    @backoff.on_exception(**BACKOFF_CONFIG)
    def _create_connection(self) -> Elasticsearch:
        """Создать новое подключение для ES"""
        return Elasticsearch([f"{self._config.host}:{self._config.port}"])

    @backoff.on_exception(**BACKOFF_CONFIG)
    def upload_data(self, data: Iterator[dict], itersize: int) -> None:
        """Загружает данные в ES используя итератор"""
        t = time.perf_counter()

        lines, _ = helpers.bulk(
            client=self.elastic_connection,
            actions=data,
            index=self._config.index,
            chunk_size=itersize,
        )

        elapsed = time.perf_counter() - t

        if lines == 0:
            logger.info("Nothing to update")
        else:
            logger.info("%s lines saved in %s", lines, elapsed)
