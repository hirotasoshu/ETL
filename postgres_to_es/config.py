import logging

import backoff
from pydantic import BaseSettings, Field

logger = logging.getLogger(__name__)


class PostgresDsn(BaseSettings):
    dbname: str = Field(..., env="POSTGRES_DB")
    user: str = Field(..., env="POSTGRES_USER")
    password: str = Field(..., env="POSTGRES_PASSWORD")
    host: str = Field(..., env="POSTGRES_HOST")
    port: int = Field(..., env="POSTGRES_PORT")
    options: str = Field(..., env="POSTGRES_OPTIONS")


class ElasticConfig(BaseSettings):
    host: str = Field(..., env="ELASTICSEARCH_HOST")
    port: int = Field(..., env="ELASTICSEARCH_PORT")
    index: str = Field(..., env="ELASTICSEARCH_INDEX")


class RedisConfig(BaseSettings):
    host: str = Field(..., env="REDIS_HOST")
    port: int = Field(..., env="REDIS_PORT")


class AppConfig(BaseSettings):
    batch_size: int = Field(..., env="BATCH_SIZE")
    frequency: int = Field(..., env="FREQUENCY")
    backoff_max_retries: int = Field(..., env="BACKOFF_MAX_RETRIES")


POSTGRES_DSN = PostgresDsn()
ELASTIC_CONFIG = ElasticConfig()
REDIS_CONFIG = RedisConfig()
APP_CONFIG = AppConfig()

BACKOFF_CONFIG = {
    "wait_gen": backoff.expo,
    "exception": Exception,
    "logger": logger,
    "max_tries": APP_CONFIG.backoff_max_retries,
}  # Роняем контейнер после n-го кол-ва ретраев, т.к. тогда он может быть перезапущен
# оркестратором в другой локации

LOGGER_SETTINGS = {
    "format": "%(asctime)s - %(name)s.%(funcName)s:%(lineno)d - %(levelname)s - %(message)s",  # noqa 501
    "datefmt": "%Y-%m-%d %H:%M:%S",
    "level": logging.INFO,
    "handlers": [logging.StreamHandler()],
}
