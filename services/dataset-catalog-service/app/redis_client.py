from typing import Optional, Any
import json
import redis.asyncio as aioredis
from app.config import settings
from app.logger import logger


class MemoryRedisMock:
    """In-memory Redis fallback mock for tests and offline environments."""

    def __init__(self):
        self._store = {}

    async def get(self, key: str) -> Optional[str]:
        return self._store.get(key)

    async def set(self, key: str, value: str, ex: Optional[int] = None) -> bool:
        self._store[key] = str(value)
        return True

    async def delete(self, key: str) -> int:
        return 1 if self._store.pop(key, None) is not None else 0

    async def setnx(self, key: str, value: str) -> bool:
        if key in self._store:
            return False
        self._store[key] = str(value)
        return True

    async def close(self):
        pass


class RedisClient:
    def __init__(self):
        self.client: Optional[Any] = None
        self._is_mock = False

    async def connect(self):
        try:
            client = aioredis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True
            )
            await client.ping()
            self.client = client
            logger.info("Connected to Redis successfully.")
        except Exception as e:
            logger.warning(f"Redis connection failed ({e}). Falling back to in-memory cache mock.")
            self.client = MemoryRedisMock()
            self._is_mock = True

    async def get_json(self, key: str) -> Optional[dict]:
        if not self.client:
            await self.connect()
        data = await self.client.get(key)
        if data:
            try:
                return json.loads(data)
            except Exception:
                return None
        return None

    async def set_json(self, key: str, value: dict, expire_seconds: int = 3600) -> bool:
        if not self.client:
            await self.connect()
        serialized = json.dumps(value)
        return await self.client.set(key, serialized, ex=expire_seconds)

    async def acquire_lock(self, key: str, lock_value: str, expire_seconds: int = 30) -> bool:
        if not self.client:
            await self.connect()
        if hasattr(self.client, "set"):
            res = await self.client.set(key, lock_value, ex=expire_seconds, nx=True)
            return bool(res)
        return await self.client.setnx(key, lock_value)

    async def close(self):
        if self.client:
            await self.client.close()


redis_client = RedisClient()
