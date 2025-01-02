from logging import getLogger
from typing import Optional

import redis
import redis.asyncio
from redis.asyncio import Redis

from src.core.settings import settings
from src.utils.singleton import SingletonMeta

logger = getLogger(__name__)


class RedisManager(metaclass=SingletonMeta):
    def __init__(self):
        self._client: Optional[Redis] = None

    @property
    def client(self) -> Redis:
        if self._client is None:
            raise Exception("no redis client provided")
        return self._client

    @client.setter
    def client(self, client: Redis) -> None:
        self._client = client

    async def connect(self) -> None:
        logger.info("Redis -> attempting to establish connection")
        self.client = await redis.asyncio.from_url(
            settings.REDIS_URL,
        )
        try:
            await self.client.ping()
            logger.info("Redis -> successfully established connection")
        except redis.ConnectionError as e:
            logger.error(
                "failed to establish redis connection, stopping application",
                extra={"error": e},
            )
            raise e

    async def disconnect(self) -> None:
        await self.client.aclose()

    def create_key(self, namespace: str, key: str) -> str:
        return f"{namespace}:{key}"
