import logging
import time
from datetime import datetime

from config import (
    APP_CONFIG,
    ELASTIC_CONFIG,
    LOGGER_SETTINGS,
    POSTGRES_DSN,
    REDIS_CONFIG,
)
from elastic_loader import ElasticLoader
from postgres_extractor import PostgresExtractor
from query import get_query
from state import RedisState

state = RedisState(config=REDIS_CONFIG)
postgres_extractor = PostgresExtractor(dsn=POSTGRES_DSN)
elastic_loader = ElasticLoader(config=ELASTIC_CONFIG, state=state)


itersize = APP_CONFIG.batch_size
freq = APP_CONFIG.frequency


def main() -> None:
    """
    Тут, видимо, требуется небольшое пояснение.
    Функция main за одно выполнение записывает не itersize записей в elastic, а все сразу.
    postgres_extractor возвращает не пачку данных, а их генератор, а elastic_loader.upload_data принимает не пачку данных, а их генератор.
    То есть, функция main записывает в elastic все записи, которые мы получили из нашего запроса.
    Itersize в postgres_extractor.load_data: Read/write attribute specifying the number of rows to fetch from the backend at each network roundtrip during iteration on a named cursor.
    Itersize в elastic_loader.upload_data: number of docs in one chunk sent to es.

    В папке images лежит скриншот, показывающий, что за раз в elastic загружается не константное кол-во данных
    """
    load_from = state.get_key("load_from", default=str(datetime.min))
    query = get_query(load_from=load_from)
    data_generator = postgres_extractor.extract_data(query, itersize)
    elastic_loader.upload_data(data_generator, itersize)


if __name__ == "__main__":
    logging.basicConfig(**LOGGER_SETTINGS)  # type: ignore
    logger = logging.getLogger(__name__)
    while True:
        logger.info("Starting sync...")
        main()
        logger.info("Sleep for %s seconds", freq)
        time.sleep(freq)
