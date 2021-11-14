import logging
import time
from datetime import datetime

from elastic_loader import ElasticLoader
from postgres_extractor import PostgresExtractor
from query import get_query
from state import RedisState

from config import (
    APP_CONFIG,
    ELASTIC_CONFIG,
    LOGGER_SETTINGS,
    POSTGRES_DSN,
    REDIS_CONFIG,
)

state = RedisState(config=REDIS_CONFIG)
postgres_extractor = PostgresExtractor(dsn=POSTGRES_DSN, state=state)
elastic_loader = ElasticLoader(config=ELASTIC_CONFIG)


itersize = APP_CONFIG.batch_size
freq = APP_CONFIG.frequency


def main() -> None:
    load_from = state.get_key("load_from", default=str(datetime.min))
    query = get_query(load_from=load_from)
    data = postgres_extractor.extract_data(query, itersize)
    elastic_loader.upload_data(data, itersize)


if __name__ == "__main__":
    logging.basicConfig(**LOGGER_SETTINGS)  # type: ignore
    logger = logging.getLogger(__name__)
    while True:
        logger.info("Starting sync...")
        main()
        logger.info("Sleep for %s seconds", freq)
        time.sleep(freq)
