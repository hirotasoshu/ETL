from abc import abstractmethod
from typing import Optional, Protocol

import backoff
from redis import Redis

from config import BACKOFF_CONFIG, RedisConfig


def is_redis_available(redis_conn: Redis) -> bool:
    try:
        redis_conn.ping()
    except:  # noqa E722
        return False
    return True


class State(Protocol):
    """Протокол State"""

    @abstractmethod
    def set_key(self, key: str, value: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_key(self, key: str, default: Optional[str] = None) -> Optional[str]:
        raise NotImplementedError


class RedisState:
    """Реализация State, использующая Redis"""

    def __init__(self, config: RedisConfig, redis_conn: Optional[Redis] = None) -> None:
        self._config = config
        self._redis_connection = redis_conn

    @property
    def redis_connection(self) -> Redis:
        """Использует текущее соединение или создает новое"""
        if not self._redis_connection or not is_redis_available(self._redis_connection):
            self._redis_connection = self._create_connection()
        return self._redis_connection  # type: ignore

    @backoff.on_exception(**BACKOFF_CONFIG)
    def _create_connection(self) -> Redis:
        """Создает новое соединение к Redis"""
        return Redis(**self._config.dict())

    @backoff.on_exception(**BACKOFF_CONFIG)
    def set_key(self, key: str, value: str) -> None:
        """Создает пару ключ-значение в Redis"""
        self.redis_connection.set(key, value.encode())

    @backoff.on_exception(**BACKOFF_CONFIG)
    def get_key(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Получение значения по ключу"""
        data = self.redis_connection.get(key)
        if data:
            return data.decode()
        return default
