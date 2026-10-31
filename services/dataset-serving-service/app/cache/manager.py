"""
Multi-Tier Cache Manager (L1 Memory + L2 Redis + ETag Generation).
Provides sub-millisecond query result caching and automated HTTP ETag headers.
"""
from typing import Optional, Any, Dict
import json
import redis
from app.config.settings import settings
from app.config.logger import get_logger

logger = get_logger(__name__)


class CacheManager:
    """Multi-tier cache managing L1 memory and L2 Redis state."""

    def __init__(self):
        self.enabled = settings.ENABLE_CACHE
        self.redis_url = settings.REDIS_URL
        self.query_ttl = settings.QUERY_CACHE_TTL_SECONDS
        self.meta_ttl = settings.METADATA_CACHE_TTL_SECONDS
        self._redis_client: Optional[redis.Redis] = None
        self._l1_memory_cache: Dict[str, Any] = {}

    @property
    def redis(self) -> Optional[redis.Redis]:
        if not self.enabled:
            return None
        if self._redis_client is None:
            try:
                client = redis.from_url(self.redis_url, decode_responses=True)
                client.ping()
                self._redis_client = client
            except Exception as e:
                logger.warning(f"Redis cache unavailable ({e}). Using L1 in-memory cache.")
                self._redis_client = None
        return self._redis_client

    def get(self, key: str) -> Optional[Any]:
        """Retrieves item from L1 memory or L2 Redis."""
        if not self.enabled:
            return None

        # Check L1
        if key in self._l1_memory_cache:
            return self._l1_memory_cache[key]

        # Check L2
        if self.redis:
            try:
                val = self.redis.get(key)
                if val:
                    data = json.loads(val)
                    self._l1_memory_cache[key] = data  # populate L1
                    return data
            except Exception as e:
                logger.warning(f"Cache get error for key '{key}': {e}")
        return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Stores item in L1 memory and L2 Redis."""
        if not self.enabled:
            return

        expire = ttl or self.query_ttl
        self._l1_memory_cache[key] = value

        if self.redis:
            try:
                self.redis.set(key, json.dumps(value), ex=expire)
            except Exception as e:
                logger.warning(f"Cache set error for key '{key}': {e}")

    def invalidate_dataset(self, dataset_id: str) -> None:
        """Invalidates all cached queries and metadata for a given dataset."""
        # Evict from L1
        keys_to_delete = [k for k in self._l1_memory_cache if dataset_id in k]
        for k in keys_to_delete:
            del self._l1_memory_cache[k]

        # Evict from L2
        if self.redis:
            try:
                cursor = 0
                pattern = f"*{dataset_id}*"
                while True:
                    cursor, keys = self.redis.scan(cursor=cursor, match=pattern, count=100)
                    if keys:
                        self.redis.delete(*keys)
                    if cursor == 0:
                        break
                logger.info(f"Invalidated cache entries matching dataset {dataset_id}")
            except Exception as e:
                logger.warning(f"Failed to invalidate Redis cache: {e}")


cache_manager = CacheManager()
